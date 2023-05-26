# PARTDAGE PROJECT


## Project presentation – *Présentation du projet*
EN: PARTDAGE is a web application (Django + postgreSQL) which allows to share experiences of life and learn from other users experiences. I deployed PARTDAGE on heroku (https://partdage.herokuapp.com/).   
The present project is a way to continue to learn and practice coding after passing a Developer degree. It is a simple application with interesting details. This application is also a concrete demonstration of my skills, in the context of a new professionnal opportunity research. And also I like to code.   

FR : *PARTDAGE est une application web (Django + postgreSQL), permettant de partager ses expériences de vie et d’apprendre des expériences des autres utilisateurs. J’ai déployé PARTDAGE sur heroku (https://partdage.herokuapp.com/).*   
*Le présent projet est l’opportunité pour moi de continuer à pratiquer le développement informatique et à apprendre après la formation de Développeur que j’ai menée à bien. Il s’agit d’une application simple mais ayant ses subtilités. Cette application constitue également une démonstration concrète de mes competences pour ma recherche d'une nouvelle opportunité professionnelle. Et puis je m'épanouis en développant, tout simplement.*   

How does it work ? Each user can share an experience of life for each age he/she lived. Each user can consult sharings (from other user) which correspond to his/her current age (+/- 1 year old). The more an user shares, the more he/she has access to now credits in the form of access to new sharings of experience.

*Comment ça marche ? Chaque utilisateur peut partager une expérience de vie pour chaque age qu’il a vécu. Chaque utilisateur peut consulter des partages d’expériences d’autres utilisateurs, qui correspondent à son âge actuel (+/- un an). Plus un utilisateur partage ses expériences, plus il a accès à de nouveaux crédits qui se concrétisent par un accès à de nouveaux partages d’expériences.*


## Specifications
I wrote specifications for the present application. The main ones are as follow:
- an user must not be able to modify the sharing of experience of another user;
- an user must not be able to share an experience corresponding to his/her current age (or older) ;
- a sharing of experience can be displayed only if the moderator approved its content.

*J’ai écrit des spécifications pour la présente application. Les principales sont les suivantes :*
- *un utilisateur ne doit pas pouvoir modifier le partage d’expérience d’un autre utilisateur ;*
- *un utilisateur ne doit pas pouvoir partager une expérience pour son âge actuelle ou un age plus avancé ;*
- *un partage d’expérience n’est affiché que s’il est validé par le modérateur.*

The web applications allows the user to : 
- Sign up and log
- chose an experienced age and write an experience of life
- read sharings of experience from other user

*L’application permet à un utilisateur de :*
- *s’inscrire et se connecter*
- *sélectionner un âge vécu et écrire une expérience de vie*
- *lire des expériences de vies d’autres utilisateurs*


## Project execution *Execution du projet*
### Prerequisites (*Prérequis*)
- Python
- A terminal
- pgAdmin4 (ideally (**idéalement))
- GitHub account with read access to this repository (*Compte GitHub avec accès en lecture à ce repository*)
- Git CLI

### Code importation *Import du code*
First of all, you must import code.

1. Optionnal step : Duplicate the project by creating a new repo in your GitHub account (*Étape optionnelle : Dupliquer le projet en créant un nouveau repo dans votre compte GitHub.*)
Click on the « Fork » button in the top right-hand corner and click « Create fork » (*Cliquez sur le bouton Fork en haut à droite et cliquez sur le bouton « Create fork »*) 
The code is now also on your github account (*Le code est désormais également disponible sur votre compte github*)

2. Create a local copy of the previous fork (créer une copie locale du fork)
Click on the "code" button, then copy the project URL; open a terminal and run : (*Cliquez sur le bouton « code », puis copiez l’URL du projet ; ouvrez un terminal et executez la commande suivante :*)
>`git clone PROJECT_URL`
You have retrieved the project locally from your github repository (*Vous avez récupéré le projet en local depuis votre repository github*).

### Local execution *Execution du code en local*
To correctly execute the program, you need to activate the associated virtual environment which has been recorded in the ‘requirements.txt’ file.
*Pour exécuter correctement le programme, vous devez activer l'environnement virtuel associé qui a été enregistré dans le fichier 'requirements.txt'.*

### Creation and activation of the virtual environment (*Création et activation de l'environnement virtuel*)
Please follow theses instructions (*Veuillez suivre les indications suivantes*):

1. Open your Shell (*ouvez votre terminal*)
-Windows: 
>'windows + R' 
>'cmd'  
-Mac: 
>'Applications > Utilitaires > Terminal.app'

2. Find the folder which contains the program (with *cd* command) (*Trouver le dossier qui contient le programme (avec la commande `cd`)*)

3. Create a virtual environment: write the following command in the console (*Créer un environnement virtuel : écrire la commande suivante dans la console *)
>'python -m venv env'

4. Activate this virtual environment (*Activez l’environnement virtuel*): 
-Linux or Mac: write the following command in the console (*saisissez la commande suivante*)
>'source env/bin/activate'
-Windows: write the following command in the console (*saisissez la commande suivante*)
>'env\Scripts\activate'

5. Install the python packages recorded in the *requirements.txt* file : write in the console the following command (*Installez les paquets python enregistrés dans le fichier *requirements.txt* : saisissez la commande suivante*)
>'pip install -r requirements.txt'

### To launch the server locally (*Lancez le serveur en local*)
Write in the console the following command (*saisissez la commande suivante*)
6. Write the following command in the console (Python must be installed on your computer and virtual environment must be activated) (*saisissez la commande suivante (Python doit être installé sur votre ordinateur et l'environnement virtuel doit être activé.)*)
>'python manage.py runserver'

### To access to the web application (*Pour accéder à l’application*)
7. Open an internet browser and visit local host url ( http://127.0.0.1:8000/ ) (*Ouvrez un navigateur Internet et visitez l'url de l'hôte local ( http://127.0.0.1:8000/ )*)

### Linting, testing and access to local database and adminitration panel (*Linting, Testing et accès à la base de données locale et au panneau d’administration*)
#### Linting
Write in the console the following command (*saisissez la commande suivante*)
- ` flake8 --max-line-length 119 --exclude=env,venv,./authentication/migrations,./sharingofexperience/migrations`

#### Tests unitaires
Write in the console one of the following command (*saisissez une des commandes suivante*)
- `pytest`
- `pytest -v`

#### Base de données
pgAdmin4 configuration is required for this step (*la configuration de pgAdmin4 est requise pour cette étape*)
You will have access to your local database by writing the following command in the console (*Vous aurez accès à votre base de données local en saisissant la commande suivante*)
- `heroku pg :psql`
You can now execute a SQL request, as an example (*Vous pouvez désormais executer une requête SQL, par exemple*)
- `SELECT * FROM sharingofexperience_sharingofexperience;`

#### Panel d'administration
- create a Django superuser (*créez un superuser Django*)
- Visite (*Allez sur*) : `http://localhost:8000/admin`
- Log in with super user credentials (*Connectez-vous avec l’authentifiant du superuser*) 


## Heroku deployment *Déploiement sur Heroku*

### Récapitulatif haut niveau du fonctionnement du déploiement
Deployment of the code on Heroku is automated via a circleCI pipeline, which is executed when a git push is made (master branch only). The circleCI pipeline is described in the .circleci/config.yml file. To use this process, you must configure your circleCI account (link it to your github account and define the HEROKU_API_KEY, HEROKU_APP_NAME and SECRET_KEY environment variables).
Deployment can also be carried out manually (see text below).

*Le déploiement du code sur Heroku est automatisé via le pipeline circleCI, qui est exécuté lors d'un push sur GitHub (branche master, uniquement). Le pipeline circleCI est décrit dans le fichier .circleci/config.yml.*
*Pour cela, vous devez configurer cotre compte circleCI (le lier à votre compte github et définir les variables d’environnement HEROKU_API_KEY ; HEROKU_APP_NAME et SECRET_KEY).*
*Le déploiement peut également se faire manuellement (voir texte ci-dessous).*

### Required configuration for deployment - *Configuration requise pour le déploiement*
Pour un déploiement manuel :
- A Heroku account
- Heroku CLI 
- A circleCI account (Un compte circleCI)

### Steps for a new heroku deployment (*Étapes nécessaires au déploiement d'une nouvelle application heroku*)
Using the terminal, go to the project folder (command `cd`), then execute the following commands: (*Avec le terminal, placez vous dans le dossier du projet (commande `cd`), puis executez les commandes suivantes :*)

- Authenticate yourself (*Authentifiez vous*)
>`heroku login`
- 
Create a heroku application (you can specify an application name ; if not, you will get a randomly generated name for this application; the notation NOM_APP_HEROKU will be used hereafter) (*Créer une application heroku (vous pouvez spécifier un nom d'application ; sinon, vous obtiendrez un nom généré aléatoirement pour cette application ; la notation NOM_APP_HEROKU sera utilisée par la suite)*)
>`heroku create NOM_APP_HEROKU`
- Make sure you are on the right "git remote" (git remotes are versions of your repository on other servers). (*Assurez vous d'être sur le bon "git remote" (les git remotes sont des versions de votre repository sur d'autres serveurs)*)
>`heroku git:remote -a NOM_APP_HEROKU`

- You can now add your environment variables to heroku (in the settings/config vars section of your application): add the SECRET_KEY variable: (*Vous pouvez désormais ajouter vos variables d’environnement sur heroku (partie settings/config vars de votre application) : ajoutez la variable SECRET_KEY:*)
- clé SECRET_KEY : ask the person responsible for the application  (*demandez la au responsable de l'application*)
- DEBUG : False
- DATABASE_URL : automatically filled in by heroku (*renseigné automatiquement par heroku*)

- Make sure you are authentified, if not : (*assurez vous d’être authentifiez, sinon *) 
>`heroku login`
- Push your code on github (*poussez votre code sur github*):
>` git add .`
>`git commit -m "MESSAGE"`
>`git push origin main` (or `git push -u origin BRANCH_NAME`)
- Push your code on heroku (*poussez votre code sur heroku *):
>`git push heroku main` (or `git push heroku BRANCH_NAME:main`)

-You can check that the application is working correctly by using the following commands (the application requires Heroku "dynos" to be available on your account) (* Vous pouvez vérifier le bon fonctionnement de l'application avec les commandes (l'application nécéssite que des "dynos" heroku soient disponible sur votre compte)*) : 
>`heroku ps:scale web=1`
>`heroku open`

### Étapes nécessaires au déploiement d'une mise à jour d'une application heroku
#### Déploiement mannuel
- To deploy a manual update (*Pour le déploiement d'une mise à jour mannuel*) :
>`heroku login`
>` git add .`
>`git commit -m "MESSAGE"`
>`git push origin main` (or `git push -u origin BRANCH_NAME`)
>`git push heroku main` (or `git push heroku BRANCH_NAME:main`)

#### Automatic deployment with a circleCI pipeline (*Déploiement automatique avec un pipeline circleCI*)
If your code is pushed to GitHub and your circleCI account is associated with your GitHub account, you should find your project on the circleCI dashboard and be able to click a "Set Up Project" button next to your project name. You can follow the documentation to initiate your pipeline (choose the 'Fastest' option)
*Si votre code est poussé sur GitHub et que votre compte circleCI est associé à votre compte GitHub, vous devriez trouver votre projet sur le tableau de bord de circleCI et avoir la possibilité de cliquer un bouton "Set Up Project" à côté du nom de votre projet. Vous pouvez suivre la documentation pour initier votre pipeline (choix de l'option 'Fastest')*

- In the circleCI project parameters, configure the following environment variables (project settings/environment variables) (*Dans les parametres du projet circleCI, configurez les variables d'envionnement (project settings/environment variables) suivantes*) :
  - HEROKU_API_KEY : your Heroku token, you can obtain a new one with the command `heroku auth:token` (*votre token Heroku, vous pouvez en obtenir un nouveau avec la commande `heroku auth:token`*)
  - HEROKU_APP_NAME : the name of your Heroku application  (*le nom de votre application Heroku*)
  - SECRET_KEY : ask the person responsible for the application  (*demandez la au responsable de l'application*)

- To make an automatic deployment with a circleCI pipeline (*Pour le déploiement automatisé d'une mise à jour*) :
>`git add .`
>`commit -m "DESCRIPTIF_DE_VOTRE_COMMIT" `
>`git push origin main` (or `git push -u origin BRANCH_NAME`)
