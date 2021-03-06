title: YAAC
menu-position: 3
type:subpage
subtitle:ouvertures
path:achem
---


# Réflexions, choix et ouvertures

Cette partie sera un peu fouillis


## Arguments pour le réseau de pétri

Les réseaux de pétri forment donc le modèle de calcul utilisé par
les bactéries pour fonctionner, interagir et se dupliquer.

Nous allons ici développer quelques arguments pour soutenir 
ce choix.

-   Le réseau de pétri est formé de manière non linéaire à partir d'une 
    liste d'acides. Cela devrait le rendre peu vulnérable à des 
    modifications mineurs de la liste d'acides formant la protéine.
    
    Reste cependant le fait que les protéines sont formées à partir 
    d'une liste d'atomes, qui est elle sensible à des variations locales.

-   Du fait de sa forme de graphe, le réseau de pétri peut être associé
    à une certaine spatialité. Par exemple, une protéine connectée à
    la membrane peut avoir une partie à l'intérieur, et une autre partie
    à l'extérieur de la membrane.

-   On peut sans trop de difficultés connecter des réseaux de pétri 
    entre eux (bind/catch), permettant d'étendre leur fonctionnalités,
    ainsi que de créer des **membranes**.


## Forme des molécules


### Molécule linéaire

Le modèle le plus simple pour une molécule est simplement d'avoir
une molécule linéaire (une liste).
Des suites d'atomes sont alors interprétées directement comme 
des acides, les atomes suivants pouvant donner de l'information 
supplémentaire, etc.

Mais le problème, 


### Molécule sous forme de graphe

Ce qui serait joli, ce serait d'avoir des connecteurs (à deux ou 
trois branches), et des morceaux d'information, mais plus 
compliqué à manipuler; il pourrait être intéressant de comparer 
avec une structure linéaire pour les molécules.


## Membrane

La membrane est une partie essentielle d'une bactérie, puisqu'elle 
la définit en établissant une barrière avec le monde extérieur.

Pour l'implémentation d'une membrane, les fonctionnalités désirées 
sont :

-   Permettre à la bactérie de réguler les entrées/sorties de

molécules

-   Établir une barrière *difficile* à franchir pour les molécules
    extérieures non désirées.
-   Avoir un taille nécéssaire en fonction de la quantité de

molécules présentes, sous risque d'effets néfastes.

Idée : Implémenter dans les cellules deux bornes qui doivent 
être reliées par un certain nombre de protéines.
(il faut que les protéines puissent se lier entre elles avec 
des catch/bind)


### Membranes avec des bind

Une extension Bind d'une place permet à deux réseaux de pétri 
de se lier. Le design de cette extension est fait de sorte 
à pouvoir facilement implémenter des membranes

Une Bind extension possède simplement une string, et se colle
à une string symétrique :

-   reversed ? -> le plus simple
-   symétrie des atomes ? -> pourquoi, pourquoi pas ?

Condition pour Binder : Les places sont vides
Après le Bind, des token sont crées. -> cela permet d'effectuer
une action après le  bind.

Condition pour DéBinder : deux token reviennent, puis sont consommés.

Deux réseaux de pétri bindés sont donc liés physiquement dans l'espace.

Se présentent alors plusieurs choix :

-   un Bind FORT : les réseaux de pétri sont fusionnés à la Place
    de Bind, ce qui permet de créer de nouveaux réseaux plus 
    compliqués
    -> c'est assez compliqué à gérer, deux places sont fusionnées,
    il faut aussi pouvoir débinder, bref garder beaucoup en mémoire
    et avoir des structures de données compliquées
-   un Bind FAIBLE : les réseaux de Pétri sont indépendants
    -> c'est assez simple, et ça peut suffire pour les membranes

Dans tous les cas, il faut créer un graphe sur-jacent qui va garder 
en mémoire la structure de la molécule, pour pouvoir travailler sur 
la structure (détecter les cycles, la distance entre deux pnet, etc).


## Ribosome

Un ribosome est une protéine qui lit un code génétique (ADN) et 
construit des protéines en fonction de l'information contenue dans 
l'ADN.

Donc pour implémenter un ribosome, il faut être capable de lire de
l'information contenue dans une molécule, de l'interpréter pour 
recoller les bons acides au bon endroit sur une molécule en train
d'être construite.

1.  Implémentation possible d'un ribosome :

    La molécule en train d'être construite se trouve à mol\_start\_place, 
    et le brin d'ADN lu se trouve à DNA\_start\_place.
    
    Les arcs entrants de transition qui partent de DNA\_start\_place sont 
    filtrants (fonctionnalité qui reste à implémenter), donc seule une 
    des filter\_transition\_i peut être lancéé (celle qui correspond à 
    l'information lue sur le brin d'ADN). 
    
    Lorsqu'une de ces transitions est lancée, la molécule se retrouve à 
    mol\_temp\_place\_i, d'où elle va être lancée vers bind\_transition\_i, 
    qui lui accolera l'acide correspondant, et enfin rejoindre 
    mol\_end\_place (commun à tous les chemins).
    
    Il suffit ensuite de faire revenir la molécule et l'ADN à leur 
    place de départ (en ayant fait bouger la tête de lecture sur l'ADN) 
    pour recommencer l'opération avec le morceau d'information suivant.
    
    Voir le résultat du code suivant pour le graphe du réseau de pétri
    décrit, où les chemins que peut suivre la molécule sont en rouge, 
    les chemins que peut suivre le brin d'ADN est en bleu, et les acides
    en vert.
    
        digraph G {
                mol_place[color = "red"]
                DNA_place[color = "blue"]
        
                transition_A[shape = "rectangle"]
                transition_B[shape = "rectangle"]
        
                atom_graber_A[color = "green"]
                atom_graber_B[color = "green"]
        
                mol_place -> transition_A ->
                mol_place  [color =red];
        
                mol_place -> transition_B ->
                mol_place [color = "red"];
        
                DNA_place -> transition_A
                [label = "filter A", color = blue];
        
                DNA_place -> transition_B
                [label = "filter B", color = blue];
        
                transition_A -> DNA_place
                [color = blue];
        
        
                transition_B -> DNA_place
                [color = blue];
        
                atom_graber_A -> transition_A [color = "green"];
                atom_graber_B -> transition_B [color = "green"];
        
        }


## Bacterie

Une bacterie contient des molécules. Pour chaque molecule, on 
connait le nombre présent, et on simule une unique forme protéinée 
pour toutes les molécules du même type.

1.  Note : on pourrait imaginer d'autres formes d'interprétation :

    -   fonction (par ex log) du nombre de mols
        -   ou autre.
    
    La simulation est alors découpée en (pour l'instant) deux étapes :
    
    -   Simulation des protéines
    -   Résolution des catch/bind


### Simulation des protéines

La protéine associée à chaque molécule lance un certain nombre
de transitions de son réseau de pétri. Pour choisir ce nombre,
on pourrait :

-   le faire correspondre au nombre de mol présentes

(ou une fonction de celui-ci

-   Prendre le pgcd de tous les nombres de molécules

(ou même diviser par le plus petit et arrondir)
pour que le coût de simulation ne dépende pas du 
nombre de molécules).


### Résolution des catch/bind

On calcule combien de bind sont effectués.

Pour le déroulé du bind en lui même, on peut aussi avoir
plusieurs choix :

-   Le bind crée un token
-   Le bind peut seulement se dérouler si un token vide

se trouve sur la place avec le catcher

-   Si un token occupé par une molécule se trouve sur la

place, la molécule est remplacée, ou alors une des deux 
au hasard.

1.  Note : du coup pour le simulateur

    On calcule les catch/bind, puis
    on attribue à chaque molécule un certain
    nb de transitions. On peut alors soit
    observer les transitions de chaque molécule,
    soit tout exécuter, etc.


## Le monde

Quelques idées : 

-   les bactéries peuvent se duppliquer sans restriction physique.
    À chaque nouvelle bactérie créée on attribue une certaines
    distribution des différentes ressources (acides aminés ?)
-   Matrice (tridimensionnelle), avec des « commandes » pour 
    interagir avec les cellules voisines, se déplacer,
    communiquer, etc..
-   Hôtes pour simuler un comportement multicellulaire : 
    l'hôte a différents emplacements pour cellules, où 
    se trouvent  des recepteurs particuliers, qui permettent
    à l'hôte d'effectuer des actions dans un autre monde physique.
-   Graphe (lazy ?) ou les nœuds contiennent pour chaque arc une 
    interface permettant de simuler une membrane. On peut imaginer
    différentes interfaces, avec différents niveaux de « difficulté ».


## Énergie

Les tokens peuvent être un bon moyen de gérer les échanges 
énergétiques. Le mieux serait sans-doute de faire comme en vrai, 
c'est à dire qu'établir un liaison coûte de l'énergie, qui est 
libérée lorsque la liaison est rompue. Ça implique de modifier un 
peu le condition de grab et de catch/bind, mais ça devrait se faire 
pas trop difficilement.
On peut aussi penser à faire des transferts d'énergie entre une 
protéine et la molécule grabée.


## Dans un futur lointain

Pour que les bactéries puissent avoir un comportement efficace, il 
faudrait qu'il y ait de l'information ambiante, qui représente 
plusieurs aspects du monde alentour, que les bactéries puissent 
mesurer

Implémenter un système similaire à tierra, où les bactéries qui 
font des actions « interdites » reçoivent un malus, et finissent
par mourir ?
(par exemple : problème de transition, problème lors du décalage
d'une molécule à l'intérieur d'

