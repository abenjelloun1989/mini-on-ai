// The story of Paper Voyage: Boats, second draft. Sources for the history cards are in ../histoires/bateaux.md.
const HISTOIRES = {
  fr: {
    intro: ["Dans son phare, la capitaine Maren écrivait pour ne rien oublier. Soixante ans de mer tenaient dans un seul livre.",
      "Depuis quelque temps, les noms lui échappaient. Les ports. Les bateaux. Alors, le livre se souvenait pour elle.",
      "Au petit matin, le vent entra. Il voulait juste regarder. Mais toutes les pages s'envolèrent.",
      "Quand il se calma, il n'en restait qu'une : la toute première. Le vent la plia en bateau. Il ne savait pas réparer autrement.",
      "Le vent porte les voix. Celle de Maren le suivit : « Commence par le plus ancien. C'est ce que j'oublierai en dernier. »"],
    fin: ["Le bateau de papier atteignit le pied du phare. Il flottait encore, à peine.",
      "La capitaine remit chaque page à sa place. Chaque nom lui revint. Il manquait une page : la toute première.",
      "Elle prit le bateau mouillé et le déplia lentement. C'était son écriture d'enfant.",
      n => (n ? `Elle recolla la page en tête du livre, avec tous ses plis. Dessous, elle écrivit : « Le plus petit de tous. Équipage : un vent nommé ${n}. »` : "Elle recolla la page en tête du livre, avec tous ses plis. Dessous, elle écrivit : « Le plus petit de tous. Capitaine : personne. Équipage : un vent. »"),
      "Puis elle plia une feuille neuve et la posa sur le rebord.",
      "Cette fois, elle laissa la fenêtre ouverte. « On y retourne ? »"],
    fin2: ["Au dos du dragon, un autre dessin : un phare, une vieille femme, le vent.",
      "Dessous, d'une main de huit ans : « Moi, plus tard. »",
      "Elle l'avait dessiné avant de te connaître.",
      "Une lettre glissa du livre.",
      "« Maren, as-tu vu mes cartes ? Tout s'est envolé par la fenêtre. Félix. »",
      "Le rideau cessa de bouger."],
    chapitres: [
      { titre: "Les premiers bateaux", depart: "« Commence par le plus ancien. C'est ce que j'oublierai en dernier. »", trouve: "Maren revoit une rivière et un tronc creusé. Plus que quatre.", bateaux: [
        ["Pirogue", "Préhistoire", "Un tronc, du feu, de la patience. Une pirogue de plus de 9 500 ans a été retrouvée aux Pays-Bas en 1955, pendant la construction d'une autoroute. Elle mesure à peine 3 mètres."],
        ["Barque de papyrus", "Égypte ancienne", "Sur le Nil, on liait des bottes de papyrus pour en faire des bateaux. Plus tard, bien des navires en bois ont gardé cette silhouette aux extrémités relevées."],
        ["Coracle", "Pays de Galles", "Un petit bateau presque rond, si léger qu'un pêcheur le porte seul. Au pays de Galles, deux coracles tendent un filet entre eux pour pêcher sur la rivière."]] },
      { titre: "Mers et canaux", depart: "« Ici, c'étaient les rameurs qui faisaient tout. Ne te vexe pas. »", trouve: "Elle sent encore le sel. Maren retrouve un prénom.", bateaux: [
        ["Trirème", "Grèce antique", "Environ 170 rameurs sur trois étages, qui devaient tous tirer sur leur rame au même moment. Essaie donc d'applaudir en rythme avec 170 personnes."],
        ["Jonque", "Chine", "Sa coque était divisée en compartiments : un trou n'inondait pas tout le bateau. Ses grandes voiles étaient renforcées de lattes."],
        ["Gondole", "Venise", "Regarde bien : une gondole est de travers. Elle est plus large et plus longue à gauche, pour aller droit avec une seule rame, placée à droite."]] },
      { titre: "Les grands voyages", depart: "« Certains marins ne savaient pas où ils allaient. C'est pour ça qu'ils sont partis. »", trouve: "Elle était sur un toit. Maren se souvient de sa première tempête.", bateaux: [
        ["Drakkar", "Vikings", "Du bois coupé par des Vikings à Terre-Neuve a été daté de 1021 grâce à une tempête solaire inscrite dans les cernes des arbres. Presque cinq siècles avant Colomb."],
        ["Caravelle", "XVe siècle", "Ses voiles triangulaires lui permettaient de remonter le vent en zigzag. Une excellente nouvelle pour les marins, et une vexation pour le vent."],
        ["Navire au trésor", "Chine, 1405", "L'amiral Zheng He a mené sept grandes expéditions de 1405 à 1433. Les vieux livres parlent de navires de plus de 130 mètres. Les historiens en discutent encore."]] },
      { titre: "Les routes du commerce", depart: "« Il fait froid. Même les meilleurs marins avaient froid. »", trouve: "Un peu gelée, mais toujours lisible. La capitaine retrouve le goût du thé à bord.", bateaux: [
        ["Galion", "1565–1815", "Pendant 250 ans, des galions ont traversé le Pacifique entre Manille et Acapulco : soie et porcelaine dans un sens, pièces et lingots d'argent dans l'autre."],
        ["Clipper", "1869", "Le Cutty Sark pouvait parcourir 363 milles nautiques en un jour. Mais il n'a jamais été le premier à rapporter le thé : en 1872, alors qu'il était en tête, il a perdu son gouvernail en pleine mer."]] },
      { titre: "L'âge de la vapeur", depart: "« Un jour, les bateaux n'ont plus eu besoin de toi. Moi, si. »", trouve: "La dernière. Au loin, la lumière du phare.", bateaux: [
        ["Bateau à aubes", "XIXe siècle", "En 1811, le premier bateau à vapeur du Mississippi a quitté Pittsburgh. En route, son équipage a vécu une série de tremblements de terre."],
        ["Paquebot", "Vers 1910", "Sur certains grands paquebots, la quatrième cheminée n'était reliée à aucune chaudière. Elle servait à aérer le navire, et à lui donner plus d'allure."]] },
      { titre: "Enfance : les petits marins", depart: "« Tu en as emporté d'autres, cachées dans la reliure. Ne les lis pas. »", trouve: "Une écriture toute de travers et une note à la plume.", bateaux: [
        ["Coquille de noix", "Maren, 8 ans", "« Pour les marins très petits. » À la plume : « Au large, on l'est tous. »"],
        ["Bicorne", "Maren, 8 ans", "« Mon chapeau est tombé à l'eau. Il flotte. » À la plume : « Quelques plis de plus, et c'était un bateau. »"]] },
      { titre: "Enfance : la basse-cour", depart: "« Ne ris pas. J'avais huit ans. »", trouve: "La page frémit. Ce n'est pas le froid.", bateaux: [
        ["Cocotte", "Maren, 8 ans", "« Elle pond pendant les tempêtes. » À la plume : « Vérifié au cap Horn : non. »"],
        ["Sabot", "Maren, 8 ans", "« Celui de mon père. Il ne le sait pas encore. » À la plume : « Il ne l'a jamais su. »"]] },
      { titre: "Enfance : le confort", depart: "« À huit ans, je croyais qu'on emportait sa maison en mer. »", trouve: "Une tache de confiture. Elle a soixante-dix ans.", bateaux: [
        ["Théière", "Maren, 8 ans", "« Pour ne jamais manquer de thé en mer. » À la plume : « J'avais raison. On en manque. »"],
        ["Baignoire", "Maren, 8 ans", "« Comme ça, on se lave pendant le voyage. » À la plume : « Quatre mois sans bain. J'y ai repensé. »"]] },
      { titre: "Enfance : le grand navire", depart: "« Celui-là, j'ai fini par le commander. »", trouve: "Le dessin prend deux pages.", bateaux: [
        ["Navire à fanions", "Maren, 8 ans", "« Le mien aura des fanions partout. » À la plume : « Le mien n'en a jamais eu. »"]] },
      { titre: "Enfance : le dragon", depart: "« La dernière. Ce dragon, je l'ai cherché pendant des années. »", trouve: "Elle est pliée en quatre, avec beaucoup de soin.", bateaux: [
        ["Dragon", "Maren, 8 ans", "« Il ne mange personne. Il est juste très grand. » À la plume : « Je ne l'ai pas trouvé. J'ai trouvé le reste. »"]] },
    ],
  },
  en: {
    intro: ["In her lighthouse, Captain Maren wrote everything down so she would forget nothing. Sixty years at sea, kept in a single book.",
      "Lately, names had been slipping away from her. Harbours. Boats. So the book remembered for her.",
      "Early one morning, the wind came in. It just wanted to look. But every page flew away.",
      "When it died down, only one was left: the very first. The wind folded it into a boat. It knew no other way to make amends.",
      "The wind carries voices. Maren's followed it: \"Start with the oldest. That's what I'll forget last.\""],
    fin: ["The paper boat reached the foot of the lighthouse. It was still afloat, barely.",
      "The captain put each page back in its place. Each name returned to her. One page was missing: the very first.",
      "She took the wet boat and slowly unfolded it. It was her childhood handwriting.",
      n => (n ? `She pasted the page back at the front of the book, creases and all. Beneath it, she wrote: "The smallest of them all. Crew: one wind named ${n}."` : "She pasted the page back at the front of the book, creases and all. Beneath it, she wrote: \"The smallest of them all. Captain: nobody. Crew: one wind.\""),
      "Then she folded a new sheet and set it on the windowsill.",
      "This time she left the window open. \"Shall we go again?\""],
    fin2: ["On the back of the dragon page, another drawing: a lighthouse, an old woman, the wind.",
      "Beneath it, in an eight-year-old's hand: \"Me, later.\"",
      "She had drawn it long before she met you.",
      "A letter slipped out of the book.",
      "\"Maren, have you seen my maps? It all flew out of the window. Felix.\"",
      "The curtain stopped moving."],
    chapitres: [
      { titre: "The First Boats", depart: "\"Start with the oldest. That's what I'll forget last.\"", trouve: "Maren pictures a river and a hollowed-out log. Four to go.", bateaux: [
        ["Dugout", "Prehistory", "A log, fire and patience. A dugout over 9,500 years old was found in the Netherlands in 1955 during motorway construction. It's barely 3 metres long."],
        ["Papyrus Skiff", "Ancient Egypt", "On the Nile, bundles of papyrus were tied together to make boats. Later, many wooden boats kept the same raised ends."],
        ["Coracle", "Wales", "A small, almost round boat, so light that one person can carry it. In Wales, two coracles stretch a net between them to fish the river."]] },
      { titre: "Seas and Canals", depart: "\"Here, the rowers did all the work. Don't take it personally.\"", trouve: "It still smells of salt. Maren remembers a name.", bateaux: [
        ["Trireme", "Ancient Greece", "About 170 rowers on three levels, all pulling together. Try clapping in time with 170 people."],
        ["Junk", "China", "Her hull was split into compartments, so one hole didn't flood the whole boat. Her big sails were stiffened with battens."],
        ["Gondola", "Venice", "Look closely: a gondola is lopsided. She's wider and longer on the left, so she goes straight with just one oar on the right."]] },
      { titre: "The Great Voyages", depart: "\"Some sailors didn't know where they were going. That's why they set out.\"", trouve: "It lay on a rooftop. Maren remembers her first storm.", bateaux: [
        ["Longship", "Vikings", "Wood cut by Vikings in Newfoundland was dated to 1021, thanks to a solar storm recorded in the tree rings. Almost five centuries before Columbus."],
        ["Caravel", "15th century", "Her triangular sails let her zigzag against the wind. Great news for sailors, and rather annoying for the wind."],
        ["Treasure Ship", "China, 1405", "Admiral Zheng He led seven great voyages from 1405 to 1433. Old books speak of ships over 130 metres long. Historians still argue about it."]] },
      { titre: "The Trade Routes", depart: "\"It's cold. Even the best sailors were cold.\"", trouve: "A little frozen, but still readable. The captain remembers the taste of tea on board.", bateaux: [
        ["Galleon", "1565–1815", "For 250 years, galleons crossed the Pacific between Manila and Acapulco, carrying silk and porcelain one way, and silver coins and bars the other."],
        ["Clipper", "1869", "The Cutty Sark could cover 363 nautical miles in a day. Yet she never brought the tea home first: in 1872, while in the lead, she lost her rudder at sea."]] },
      { titre: "The Age of Steam", depart: "\"One day, boats stopped needing you. I never did.\"", trouve: "The last one. In the distance, the lighthouse beam.", bateaux: [
        ["Paddle Steamer", "19th century", "In 1811, the first Mississippi steamboat left Pittsburgh. On the way, her crew sailed through a series of earthquakes."],
        ["Ocean Liner", "Around 1910", "On some great liners, the fourth funnel wasn't connected to any boiler. It helped air the ship and made her look grander."]] },
      { titre: "Childhood: Tiny Sailors", depart: "\"You carried off others too, hidden in the binding. Don't read them.\"", trouve: "Crooked handwriting and a note in ink.", bateaux: [
        ["Walnut Shell", "Maren, aged 8", "\"For very small sailors.\" In ink: \"Out at sea, we all are.\""],
        ["Bicorne", "Maren, aged 8", "\"My hat fell in the water. It floats.\" In ink: \"A few more folds and it was a boat.\""]] },
      { titre: "Childhood: The Farmyard", depart: "\"Don't laugh. I was eight.\"", trouve: "The page trembles. It isn't the cold.", bateaux: [
        ["Paper Hen", "Maren, aged 8", "\"She lays eggs during storms.\" In ink: \"Tested off Cape Horn: no.\""],
        ["Clog", "Maren, aged 8", "\"It's my father's. He doesn't know yet.\" In ink: \"He never found out.\""]] },
      { titre: "Childhood: Home Comforts", depart: "\"At eight, I thought you took your house to sea.\"", trouve: "A jam stain. It is seventy years old.", bateaux: [
        ["Teapot", "Maren, aged 8", "\"So you never run out of tea at sea.\" In ink: \"I was right. You do run out.\""],
        ["Bathtub", "Maren, aged 8", "\"That way you can wash during the voyage.\" In ink: \"Four months without a bath. I remembered this.\""]] },
      { titre: "Childhood: The Great Ship", depart: "\"That one, I ended up commanding.\"", trouve: "The drawing fills two pages.", bateaux: [
        ["Flag Ship", "Maren, aged 8", "\"Mine will have flags everywhere.\" In ink: \"Mine never had any.\""]] },
      { titre: "Childhood: The Dragon", depart: "\"The last one. I looked for this dragon for years.\"", trouve: "It has been folded into quarters, with great care.", bateaux: [
        ["Dragon", "Maren, aged 8", "\"He doesn't eat anyone. He's just very big.\" In ink: \"I never found him. I found everything else.\""]] },
    ],
  },
};
