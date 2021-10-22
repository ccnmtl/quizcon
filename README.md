[![Actions Status](https://github.com/ccnmtl/quizcon/workflows/build-and-test/badge.svg)](https://github.com/ccnmtl/quizcon/actions)

# Quizzing With Confidence

Quizcon provides an alternative question type to faculty who use multiple choice questions as part of their assessments. The platform uses confidence-weighted multiple choice questions to give students an opportunity to not only receive partial credit in a multiple choice question, but to also more directly show their level of understanding of a specific concept.

## Configuration

1. Clone

    git clone https://github.com/ccnmtl/quizcon.git
    cd quizcon

2. Create the database

   For Postgres:
     * Create a database user/password (if needed)
     * Create the database `createdb quizcon`

3. Customize settings

    * Create a local_settings.py file in the `quizcon` subdirectory OR
    * Copy `quizcon/settings_shared.py` to `quizcon/local_settings.py`
    * Then, override the variables from `settings_shared.py` that you need to customize for your local installation.
      * Customize your `DATABASES` dictionary
        * e.g. set NAME, HOST, USER, and PASSWORD. remove PORT (unless it's non-standard)
      * Specify ALLOWED_HOSTS = [ 'localhost', '.your.blackboard.or.moodle.domain', '.your.workstation.domain', ]
    * The ``PYLTI_CONFIG`` variable in your ``local_settings.py`` configures the application consumers and secrets. Generate two long random numbers for these values.

       ```
       PYLTI_CONFIG = {
           'consumers': {
               '<random number string>': {
                   'secret': '<random number string>'
               }
           }
       }
       ```
4. Build the virtual environment

   `make` will build the virtualenv

5. Migrate the database

   `./manage.py migrate`

6. Run

    `make runserver`

## LMS INSTALLATION

Canvas
* https://community.canvaslms.com/docs/DOC-13117-415274482
  * Note: the URL to enter in these steps will be `https://<app hostname>/lti/config.xml`
