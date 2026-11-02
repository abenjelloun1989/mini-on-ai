// The story of Paper Voyage: Boats. Master copy with sources in ../histoires/bateaux.md.
const HISTOIRES = {
  fr: {
    intro: ['La capitaine Maren a passé sa vie à écrire le Grand Livre des Bateaux.',
      'Un matin, un petit vent curieux entra par la fenêtre. Il voulait seulement regarder.',
      "Toutes les pages s'envolèrent. Il n'en restait qu'une, la toute première. Windy la plia en bateau : il allait tout réparer."],
    fin: ['Le Petit Papier arriva au pied du phare, trempé et très fier.',
      'La capitaine remit chaque page à sa place. Il en manquait une : la toute première.',
      'Elle prit le petit bateau mouillé, le déplia doucement et le colla dans le livre.',
      n => `Dessous, elle écrivit : « Le plus petit bateau de l'histoire. Capitaine : ${n}. Équipage : un vent. »`,
      'Puis elle plia une nouvelle feuille, et la tendit à Windy. « On y retourne ? »'],
    fin2: ['Sur la dernière page, un dessin d\'enfant : une vieille dame, un phare et un petit vent.',
      "Elle l'avait dessiné avant de te connaître.",
      'Une lettre glissa du livre. « Maren, as-tu vu mes cartes ? Tout a disparu par la fenêtre. Félix. »',
      'Windy rougit un peu.'],
    chapitres: [
      { titre: 'Les premiers bateaux', depart: '« Commence par le début, petit vent. Tout a commencé par un tronc. »', trouve: 'La capitaine sourit : « Plus que quatre. »', bateaux: [
        ['Pirogue', 'Préhistoire', 'Un tronc, du feu, de la patience. Une pirogue de plus de 9 500 ans a été retrouvée aux Pays-Bas en 1955, pendant les travaux d\'une route. Elle mesure à peine 3 mètres.'],
        ['Barque de papyrus', 'Égypte ancienne', 'Sur le Nil, on liait des bottes de papyrus pour faire flotter un bateau. Plus tard, beaucoup de bateaux de bois ont gardé cette silhouette aux extrémités relevées.'],
        ['Coracle', 'Pays de Galles', 'Un petit bateau presque rond, si léger qu\'un pêcheur le porte seul. Au pays de Galles, deux coracles tendent un filet entre eux pour pêcher sur la rivière.']] },
      { titre: 'Les mers anciennes', depart: '« Les pages aiment l\'eau chaude, et les rameurs aussi. »', trouve: 'Elle sent encore le sel.', bateaux: [
        ['Trirème', 'Grèce antique', 'Environ 170 rameurs sur trois étages, qui devaient tous tirer en même temps. Essaie donc d\'applaudir en rythme avec 170 personnes.'],
        ['Jonque', 'Chine', 'Sa coque était divisée en compartiments : un trou ne remplissait pas tout le bateau. Ses grandes voiles étaient renforcées de lattes.'],
        ['Gondole', 'Venise', 'Regarde bien : une gondole est de travers. Elle est plus large et plus longue à gauche, pour aller droit malgré sa seule rame à droite.']] },
      { titre: 'Les grands voyages', depart: '« Certains marins ne savaient pas où ils allaient. C\'est pour ça qu\'ils y sont allés. »', trouve: 'Windy a vu toute la ville depuis les toits.', bateaux: [
        ['Drakkar', 'Vikings', 'Du bois coupé par des Vikings à Terre-Neuve a été daté de 1021 grâce à une tempête solaire inscrite dans les arbres. Presque cinq siècles avant Colomb.'],
        ['Caravelle', 'XVe siècle', 'Ses voiles triangulaires lui permettaient de remonter contre le vent, en zigzag. Une excellente nouvelle pour les marins, et une vexation pour Windy.'],
        ['Navire au trésor', 'Chine, 1405', 'L\'amiral Zheng He a mené sept grandes expéditions de 1405 à 1433. Les vieux livres parlent de navires de plus de 130 mètres. Les historiens en discutent encore.']] },
      { titre: 'Les routes du commerce', depart: '« Il fait froid, petit vent. Les meilleurs marins aussi avaient froid. »', trouve: 'Un peu gelée, mais lisible.', bateaux: [
        ['Galion', '1565–1815', 'Pendant 250 ans, de 1565 à 1815, des galions ont traversé le Pacifique entre Manille et Acapulco : soie et porcelaine à l\'aller, métal argent au retour.'],
        ['Clipper', '1869', 'Le Cutty Sark pouvait parcourir 363 milles en un jour. Mais il n\'a jamais été le premier à rapporter le thé : en 1872, alors qu\'il menait, il a perdu son gouvernail en pleine mer.']] },
      { titre: "L'âge de la vapeur", depart: '« Un jour, les bateaux ont cessé d\'avoir besoin de toi. Mais pas moi. »', trouve: 'La dernière ! Windy aperçoit la lumière du phare.', bateaux: [
        ['Bateau à aubes', 'XIXe siècle', 'En 1811, le premier bateau à vapeur du Mississippi a quitté Pittsburgh. En route, son équipage a traversé une série de tremblements de terre.'],
        ['Paquebot', 'Vers 1910', 'Sur certains grands paquebots, la quatrième cheminée n\'était reliée à aucune chaudière. Elle servait à aérer le navire, et à faire plus beau.']] },
      { titre: 'Enfance : les petits marins', depart: '« Il reste des pages que je n\'ai montrées à personne. Elles sont un peu ridicules. »', trouve: 'Une écriture d\'enfant, toute de travers.', bateaux: [
        ['Coquille de noix', 'Maren, 8 ans', '« Pour les marins très petits. »'], ['Bicorne', 'Maren, 8 ans', '« Mon chapeau est tombé à l\'eau. Il flotte. »']] },
      { titre: 'Enfance : la basse-cour', depart: '« Ne ris pas. J\'avais huit ans. »', trouve: 'Windy rit quand même.', bateaux: [
        ['Cocotte', 'Maren, 8 ans', '« Elle pond pendant les tempêtes. »'], ['Sabot', 'Maren, 8 ans', '« Celui de mon père. Il ne le sait pas encore. »']] },
      { titre: 'Enfance : le confort', depart: '« À huit ans, je pensais surtout au goûter. »', trouve: 'Il y a une tache de confiture.', bateaux: [
        ['Théière', 'Maren, 8 ans', '« Pour ne jamais manquer de thé en mer. »'], ['Baignoire', 'Maren, 8 ans', '« Comme ça, on se lave pendant le voyage. »']] },
      { titre: 'Enfance : le grand navire', depart: '« Celui-là, je l\'ai vraiment cherché. Pendant des années. »', trouve: 'Le dessin prend deux pages.', bateaux: [
        ['Galion', 'Maren, 8 ans', '« Le mien aura des fanions partout. »']] },
      { titre: 'Enfance : le dragon', depart: '« La dernière. C\'est ma préférée. »', trouve: 'Elle est pliée en quatre, très soigneusement.', bateaux: [
        ['Dragon', 'Maren, 8 ans', '« Il ne mange personne. Il est juste très grand. »']] },
    ],
  },
  en: {
    intro: ['Captain Maren spent her whole life writing the Great Book of Boats.',
      'One morning, a curious little wind came in through the window. It only wanted to look.',
      'Every page flew away. Only the very first was left. Windy folded it into a boat: he would put things right.'],
    fin: ['The Little Paper reached the lighthouse, soaked and very proud.',
      'The captain put the pages back in place. One was still missing: the very first.',
      'She took the wet little boat, gently unfolded it, and glued it into the book.',
      n => `Beneath it she wrote: "The smallest boat in history. Captain: ${n}. Crew: one wind."`,
      'Then she folded a new sheet and held it out to Windy. "Shall we go again?"'],
    fin2: ['On the last page, a child\'s drawing: an old lady, a lighthouse and a little wind.',
      'She had drawn it long before she met you.',
      'A letter slipped out of the book. "Maren, have you seen my maps? They all flew out of the window. Felix."',
      'Windy blushed a little.'],
    chapitres: [
      { titre: 'The First Boats', depart: '"Start at the beginning, little wind. It all began with a log."', trouve: 'The captain smiles: "Four to go."', bateaux: [
        ['Dugout', 'Prehistory', 'A log, fire and patience. A dugout over 9,500 years old was found in the Netherlands in 1955 during roadworks. It\'s barely 3 metres long.'],
        ['Papyrus Skiff', 'Ancient Egypt', 'On the Nile, bundles of papyrus were tied together to make boats. Later, many wooden boats kept the same raised ends.'],
        ['Coracle', 'Wales', 'A small, almost round boat, so light that one person can carry it. In Wales, two coracles stretch a net between them to fish the river.']] },
      { titre: 'The Ancient Seas', depart: '"Pages love warm water. So do rowers."', trouve: 'It still smells of salt.', bateaux: [
        ['Trireme', 'Ancient Greece', 'About 170 rowers on three levels, all pulling together. Try clapping in time with 170 people.'],
        ['Junk', 'China', 'Her hull was split into compartments, so one hole didn\'t flood the whole boat. Her big sails were stiffened with battens.'],
        ['Gondola', 'Venice', 'Look closely: a gondola is lopsided. She\'s wider and longer on the left, so she goes straight with just one oar on the right.']] },
      { titre: 'The Great Voyages', depart: '"Some sailors didn\'t know where they were going. That\'s why they went."', trouve: 'Windy can see the whole town from the rooftops.', bateaux: [
        ['Longship', 'Vikings', 'Wood cut by Vikings in Newfoundland was dated to 1021, thanks to a solar storm recorded in the tree rings. Almost five centuries before Columbus.'],
        ['Caravel', '15th century', 'Her triangular sails let her zigzag against the wind. Great news for sailors, and rather annoying for Windy.'],
        ['Treasure Ship', 'China, 1405', 'Admiral Zheng He led seven great voyages from 1405 to 1433. Old books speak of ships over 130 metres long. Historians still argue about it.']] },
      { titre: 'The Trade Routes', depart: '"It\'s cold, little wind. The best sailors were cold too."', trouve: 'A little frozen, but still readable.', bateaux: [
        ['Galleon', '1565–1815', 'For 250 years, from 1565 to 1815, galleons crossed the Pacific between Manila and Acapulco, with silk and porcelain one way and silver the other.'],
        ['Clipper', '1869', 'The Cutty Sark could cover 363 nautical miles in a day. Yet she never brought the tea home first: in 1872, while in the lead, she lost her rudder at sea.']] },
      { titre: 'The Age of Steam', depart: '"One day, boats stopped needing you. I never did."', trouve: 'The last one! Windy can see the lighthouse.', bateaux: [
        ['Paddle Steamer', '19th century', 'In 1811, the first Mississippi steamboat left Pittsburgh. On the way, her crew sailed through a series of earthquakes.'],
        ['Ocean Liner', 'Around 1910', 'On some great liners, the fourth funnel wasn\'t connected to any boiler. It helped air the ship and made her look grander.']] },
      { titre: 'Childhood: Tiny Sailors', depart: '"There are pages I\'ve never shown anyone. They\'re a little silly."', trouve: 'A child\'s handwriting, all crooked.', bateaux: [
        ['Walnut Shell', 'Maren, aged 8', '"For very small sailors."'], ['Bicorne', 'Maren, aged 8', '"My hat fell in the water. It floats."']] },
      { titre: 'Childhood: The Farmyard', depart: '"Don\'t laugh. I was eight."', trouve: 'Windy laughs anyway.', bateaux: [
        ['Paper Hen', 'Maren, aged 8', '"She lays eggs during storms."'], ['Clog', 'Maren, aged 8', '"It\'s my father\'s. He doesn\'t know yet."']] },
      { titre: 'Childhood: Home Comforts', depart: '"At eight, I mostly thought about snacks."', trouve: 'There\'s a jam stain on it.', bateaux: [
        ['Teapot', 'Maren, aged 8', '"So you never run out of tea at sea."'], ['Bathtub', 'Maren, aged 8', '"This way you get washed during the trip."']] },
      { titre: 'Childhood: The Great Ship', depart: '"I really did look for this one. For years."', trouve: 'The drawing fills two pages.', bateaux: [
        ['Galleon', 'Maren, aged 8', '"Mine will have flags everywhere."']] },
      { titre: 'Childhood: The Dragon', depart: '"The last one. It\'s my favourite."', trouve: 'It\'s folded in four, very carefully.', bateaux: [
        ['Dragon', 'Maren, aged 8', '"He doesn\'t eat anyone. He\'s just very big."']] },
    ],
  },
};
