"""Grade-8 vocabulary, taken from the course book's own glossary.

res/book_8.pdf lists every unit's words on pages 169-170 under "GLOSSARY".
That list is the book's official word stock for the unit, so the decks use it
verbatim; only the Turkish meanings and the icons are added here. Entries the
glossary wraps over two lines ("get on well with / somebody") are joined back.

Shape:  unit -> [(section title, section title in Turkish, [(en, tr, emoji)…])]
"""

VOCAB = {
 1: [
  ("Friends", "Arkadaşlar", [
   ("friendship", "arkadaşlık", "❤️"), ("best friend", "en iyi arkadaş", "👯"),
   ("buddy", "dost", "🧑‍🤝‍🧑"), ("mate", "arkadaş", "🙋"),
   ("advice", "tavsiye", "💡"), ("concert", "konser", "🎤"),
   ("come over", "uğramak", "🚪"), ("go for a walk", "yürüyüşe çıkmak", "🚶")]),
  ("Qualities of Friendship", "Arkadaşlığın nitelikleri", [
   ("loyalty", "sadakat", "🤝"), ("trust", "güven", "🫱"),
   ("patience", "sabır", "⏳"), ("mutual", "karşılıklı", "↔️"),
   ("unconditional", "koşulsuz", "💗"), ("priceless", "paha biçilmez", "💎"),
   ("treasure", "hazine", "🏆"), ("secret", "sır", "🤫"),
   ("promise", "söz vermek", "🤞"), ("share", "paylaşmak", "🤲"),
   ("support", "desteklemek", "🙌"), ("count on", "güvenmek", "🫶"),
   ("back up", "arka çıkmak", "🛡️"), ("get on well with somebody", "biriyle iyi geçinmek", "😊"),
   ("survive", "hayatta kalmak", "💪")]),
  ("Describing People", "İnsanları anlatmak", [
   ("awesome", "harika", "🤩"), ("cool", "havalı", "😎"),
   ("laid-back", "rahat, sakin", "😌"), ("thrilling", "heyecan verici", "⚡"),
   ("serious", "ciddi", "😐"), ("busy", "meşgul", "📅"),
   ("full", "tok", "🍽️"), ("stuffed", "çok tok", "😋")]),
 ],
 2: [
  ("Teen Life", "Gençlik hayatı", [
   ("teenager", "genç", "🧑"), ("hang out", "takılmak", "🧑‍🤝‍🧑"),
   ("relationship", "ilişki", "🤝"), ("argue", "tartışmak", "😠"),
   ("fashion", "moda", "👗"), ("trendy", "moda olan", "✨"),
   ("snob", "züppe", "🎩"), ("concert", "konser", "🎤"),
   ("types of music", "müzik türleri", "🎵")]),
  ("Likes & Preferences", "Beğeni ve tercihler", [
   ("prefer", "tercih etmek", "⚖️"), ("fond of", "hoşlanmak", "💕"),
   ("recommend", "tavsiye etmek", "👍"), ("relaxing", "rahatlatıcı", "😌"),
   ("impressive", "etkileyici", "🌟"), ("terrific", "muhteşem", "🤩"),
   ("ridiculous", "saçma", "🙃"), ("unbearable", "dayanılmaz", "😖"),
   ("loud", "gürültülü", "🔊"), ("serious", "ciddi", "😐")]),
 ],
 3: [
  ("Cooking Verbs", "Yemek fiilleri", [
   ("bake", "fırında pişirmek", "🥧"), ("boil", "haşlamak", "🫧"),
   ("chop", "doğramak", "🔪"), ("cut", "kesmek", "✂️"),
   ("dice", "küp küp doğramak", "🎲"), ("fry", "kızartmak", "🍳"),
   ("mash", "ezmek", "🥔"), ("mix", "karıştırmak", "🌀"),
   ("peel", "soymak", "🥕"), ("pour", "dökmek", "🚰"),
   ("slice", "dilimlemek", "🍞"), ("spread", "sürmek", "🧈")]),
  ("Kitchen Tools", "Mutfak gereçleri", [
   ("bowl", "kase", "🥣"), ("grater", "rende", "🧀"),
   ("oven", "fırın", "🔥"), ("pan", "tava", "🍳"),
   ("saucepan", "tencere", "🍲"), ("spoon", "kaşık", "🥄"),
   ("oil", "yağ", "🫗"), ("ingredient", "malzeme", "🧂")]),
  ("Taste & Food", "Tat ve yemek", [
   ("recipe", "tarif", "📜"), ("meal", "öğün", "🍽️"),
   ("dessert", "tatlı", "🍰"), ("delicious", "nefis", "😋"),
   ("tasty", "lezzetli", "🤤"), ("salty", "tuzlu", "🧂"),
   ("sour", "ekşi", "🍋"), ("spicy", "baharatlı", "🌶️")]),
 ],
 4: [
  ("On the Phone", "Telefonda", [
   ("dial", "numara çevirmek", "☎️"), ("pick up", "telefonu açmak", "📞"),
   ("hang on", "hatta beklemek", "⏳"), ("hang up", "telefonu kapatmak", "📴"),
   ("hold", "beklemek", "🤙"), ("line", "hat", "📞"),
   ("engaged", "meşgul (hat)", "📵"), ("extension", "dahili numara", "🔢")]),
  ("Keeping in Touch", "İletişimde kalmak", [
   ("available", "müsait", "✅"), ("connect", "bağlamak", "🔌"),
   ("contact", "iletişim kurmak", "📇"), ("get in touch", "iletişime geçmek", "📱"),
   ("keep in touch", "iletişimde kalmak", "💬"), ("get back", "geri dönmek", "↩️"),
   ("put someone through", "birini bağlamak", "🔀"), ("memo", "not", "📝"),
   ("polite", "kibar", "🙇")]),
 ],
 5: [
  ("Internet Basics", "İnternetin temelleri", [
   ("account", "hesap", "👤"), ("browser", "tarayıcı", "🌐"),
   ("browse", "gezinmek", "🧭"), ("connection", "bağlantı", "📶"),
   ("screen", "ekran", "🖥️"), ("search engine", "arama motoru", "🔎"),
   ("social networking site", "sosyal ağ sitesi", "👥"), ("attachment", "ek dosya", "📎")]),
  ("Online Actions", "İnternette yaptıklarımız", [
   ("download", "indirmek", "⬇️"), ("upload", "yüklemek", "⬆️"),
   ("delete", "silmek", "🗑️"), ("reply", "yanıtlamak", "↩️"),
   ("comment", "yorum yapmak", "💬"), ("confirm", "onaylamak", "✔️"),
   ("register", "kayıt olmak", "📝"), ("sign up", "üye olmak", "✍️"),
   ("sign in", "giriş yapmak", "🔑"), ("log on", "oturum açmak", "🔓"),
   ("log off", "oturumu kapatmak", "🚪")]),
 ],
 6: [
  ("Extreme Sports", "Ekstrem sporlar", [
   ("extreme sports", "ekstrem sporlar", "🏂"), ("bungee-jumping", "bancî atlayışı", "🪢"),
   ("canoeing", "kano sporu", "🛶"), ("caving", "mağaracılık", "🕳️"),
   ("hang-gliding", "delta kanat", "🪁"), ("kayaking", "kayak (kano)", "🚣"),
   ("motor racing", "motor yarışı", "🏎️"), ("paragliding", "yamaç paraşütü", "🪂"),
   ("rafting", "rafting", "🌊"), ("skateboarding", "kaykay", "🛹"),
   ("take risks", "risk almak", "🎲"), ("extreme", "aşırı", "🔥")]),
  ("Describing Activities", "Etkinlikleri anlatmak", [
   ("amusing", "eğlenceli", "😄"), ("challenging", "zorlayıcı", "💪"),
   ("entertaining", "eğlendirici", "🎪"), ("exciting", "heyecan verici", "⚡"),
   ("fascinating", "büyüleyici", "✨"), ("disappointing", "hayal kırıklığı yaratan", "😞")]),
 ],
 7: [
  ("Places to Visit", "Gezilecek yerler", [
   ("destination", "gidilecek yer", "🧭"), ("attraction", "gezilecek yer", "📍"),
   ("historic site", "tarihi alan", "🏺"), ("square", "meydan", "⛲"),
   ("resort", "tatil köyü", "🏖️"), ("countryside", "kırsal kesim", "🌄"),
   ("bed and breakfast", "pansiyon", "🛏️"), ("all-inclusive", "her şey dahil", "🏨")]),
  ("Describing Places", "Yerleri anlatmak", [
   ("ancient", "antik", "🏛️"), ("architecture", "mimari", "🏗️"),
   ("culture", "kültür", "🎭"), ("cultural", "kültürel", "🎎"),
   ("fascinating", "büyüleyici", "✨"), ("incredible", "inanılmaz", "🤯"),
   ("rural", "kırsal", "🚜"), ("urban", "kentsel", "🏙️")]),
 ],
 8: [
  ("Chores at Home", "Evdeki işler", [
   ("doing chores", "ev işi yapmak", "🏠"), ("make the bed", "yatağı toplamak", "🛏️"),
   ("set the table", "sofrayı kurmak", "🍴"), ("wash the dishes", "bulaşık yıkamak", "🧼"),
   ("dry the dishes", "bulaşık kurulamak", "🌀"), ("load the dishwasher", "bulaşık makinesini doldurmak", "🍽️"),
   ("empty the dishwasher", "bulaşık makinesini boşaltmak", "📤"), ("do the laundry", "çamaşır yıkamak", "🧺"),
   ("laundry", "çamaşır", "👕"), ("iron", "ütü yapmak", "👔"),
   ("clean up", "temizlemek", "🧹"), ("tidy up", "toparlamak", "🧽"),
   ("take out the garbage", "çöpü çıkarmak", "🗑️")]),
  ("Rules & Responsibilities", "Kurallar ve sorumluluklar", [
   ("obey the rules", "kurallara uymak", "📏"), ("arrive on time", "zamanında gelmek", "⏰"),
   ("keep quiet", "sessiz olmak", "🤫"), ("keep a promise", "sözünü tutmak", "🤞"),
   ("break a promise", "sözünü bozmak", "💔"), ("return books", "kitapları iade etmek", "📚"),
   ("to-do list", "yapılacaklar listesi", "📝")]),
 ],
 9: [
  ("In the Lab", "Laboratuvarda", [
   ("lab", "laboratuvar", "🧪"), ("do an experiment", "deney yapmak", "⚗️"),
   ("test tube", "deney tüpü", "🧫"), ("cell", "hücre", "🔬"),
   ("safety", "güvenlik", "🦺"), ("scientific", "bilimsel", "📐"),
   ("process", "süreç", "🔄"), ("result", "sonuç", "📊"),
   ("explode", "patlamak", "💥")]),
  ("Science & Discovery", "Bilim ve keşif", [
   ("discover", "keşfetmek", "🔍"), ("invent", "icat etmek", "💡"),
   ("explore", "araştırmak", "🧭"), ("search", "araştırmak", "🔎"),
   ("succeed", "başarmak", "🏅"), ("genius", "dâhi", "🧠"),
   ("high-tech", "ileri teknoloji", "🤖"), ("cure", "tedavi etmek", "💊"),
   ("vaccination", "aşılama", "💉")]),
 ],
 10: [
  ("Natural Disasters", "Doğal afetler", [
   ("earthquake", "deprem", "🌎"), ("flood", "sel", "🌊"),
   ("drought", "kuraklık", "🏜️"), ("avalanche", "çığ", "🏔️"),
   ("landslide", "heyelan", "⛰️"), ("hurricane", "kasırga", "🌀"),
   ("tornado", "hortum", "🌪️"), ("tsunami", "tsunami", "🌊"),
   ("volcano", "yanardağ", "🌋"), ("disaster", "felaket", "⚠️")]),
  ("Causes & Precautions", "Sebepler ve önlemler", [
   ("global warming", "küresel ısınma", "🌡️"), ("melt", "erimek", "💧"),
   ("precaution", "önlem", "🛡️"), ("suffer", "acı çekmek", "😣"),
   ("survivor", "hayatta kalan", "🙏")]),
 ],
}


def sections(unit):
    """[(title, titleTr, [ {en, tr, emoji} … ]) …] for one unit."""
    return [(t, tr, [{"en": e, "tr": m, "emoji": ic} for e, m, ic in words])
            for t, tr, words in VOCAB.get(unit, [])]


def count(unit):
    return sum(len(w) for _, _, w in VOCAB.get(unit, []))
