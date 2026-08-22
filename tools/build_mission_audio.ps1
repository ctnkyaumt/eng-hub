param(
    [switch]$Force
)

# Generate portable WAV clips for every vocabulary card and Listen & Find item
# using an installed Windows English voice. The clips are committed with the
# app, so playback never depends on browser voices or the internet.

$projectRoot = Split-Path $PSScriptRoot -Parent
$audioRoot = Join-Path $projectRoot "app\audio\words"
New-Item -ItemType Directory -Force -Path $audioRoot | Out-Null

$clips = @{}
Get-ChildItem (Join-Path $projectRoot "content") -Recurse -Filter slides.json | ForEach-Object {
    $deck = Get-Content -Raw -LiteralPath $_.FullName | ConvertFrom-Json
    $deck.slides |
        Where-Object { $_.type -eq "vocab" } |
        ForEach-Object {
            $_.items | ForEach-Object {
                if ($_.en) {
                    $slug = ($_.en.ToLowerInvariant() -replace '[^a-z0-9]+', '-').Trim('-')
                    if ($slug) {
                        $clips["/app/audio/words/$slug.wav"] = $_.en
                    }
                }
            }
    }
    $deck.slides |
        Where-Object { $_.type -eq "mission" -and $_.task.kind -eq "listenpicture" } |
        ForEach-Object {
            $_.task.items | ForEach-Object {
                if ($_.audio -and $_.en) {
                    $clips[$_.audio] = $_.en
                }
            }
    }
}

$pending = @($clips.GetEnumerator() | Where-Object {
    $target = Join-Path $audioRoot (Split-Path $_.Name -Leaf)
    $Force -or -not (Test-Path -LiteralPath $target)
})
$skipped = $clips.Count - $pending.Count
if ($pending.Count -eq 0) {
    Write-Output ("voice: existing clips   written: 0   skipped: {0}   total: {1}" -f `
        $skipped, $clips.Count)
    return
}

Add-Type -AssemblyName System.Speech
$speaker = [System.Speech.Synthesis.SpeechSynthesizer]::new()
$voice = $speaker.GetInstalledVoices() |
    Where-Object { $_.Enabled -and $_.VoiceInfo.Culture.Name -like "en-*" } |
    Select-Object -First 1
if (-not $voice) {
    $speaker.Dispose()
    throw "No installed English speech voice was found."
}
$speaker.SelectVoice($voice.VoiceInfo.Name)
$speaker.Rate = -1
$speaker.Volume = 100

$written = 0
try {
    foreach ($entry in $pending | Sort-Object Name) {
        $filename = Split-Path $entry.Name -Leaf
        $target = Join-Path $audioRoot $filename
        $speaker.SetOutputToWaveFile($target)
        $speaker.Speak($entry.Value)
        $speaker.SetOutputToNull()
        $written++
    }
}
finally {
    $speaker.Dispose()
}

Write-Output ("voice: {0}   written: {1}   skipped: {2}   total: {3}" -f `
    $voice.VoiceInfo.Name, $written, $skipped, $clips.Count)
