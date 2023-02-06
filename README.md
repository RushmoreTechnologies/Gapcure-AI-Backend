-   ### **Project Setup**:


    -   Get repo on your local system:

        ```
        $ git clone https://github.com/KiwiTechLLC/Pytho-AI-Backend.git
        ```

    -   Install dependencies:

        ```
        $ sudo add-apt-repository ppa:deadsnakes/ppa
        $ Add following line in /etc/apt/sources.list
        $ deb http://cz.archive.ubuntu.com/ubuntu eoan main universe
        $ sudo apt update
        $ sudo apt install python3.8
        $ sudo apt install python3.8-dev
        $ sudo apt install python3-pip
        $ sudo apt install python3.8-venv
        $ git clone https://github.com/KiwiTechLLC/Pytho-AI-Backend.git
        $ git checkout dev
        $ cd Pytho-AI-Backend
        $ python -m venv /home/ubuntu/pythoai
        $ source pythoai/bin/activate
        $ pip install -r requirements.txt

        ```

    -   Launch Server:

        ```
        $ nohup gunicorn --config "gunicorn_config.py" wsgi:app &

        ```

    -   Verification:

        ```
        Run following command through shell
        $ curl --request POST \
          --url http://127.0.0.1:8000/parse \
          --header 'content-type: application/json' \
          --data '{"bucket_name":"textract-console-us-east-2-033efaad-c1f5-447b-975e-18e5d25337b6","document_name":"10.21.16_initial_ortho_visit_w_dr._mcdonald.pdf"}'

        ```

        Verify that it produces a valid 200 response code and has the following data structure. Dummy data shown so don’t worry about the exact response.

        ```json
        {
        "patient-name": "xyz",
        "file-number": "123",
        "date-of-injury": "01-15-2021",
        "dob": "03-09-1993",
        "employer":" abc",
        "ssn": "123456789",
        "provider": "xxyy",
        "icd-10-codes":{"B97.35": 10,
                        "A02.21": 15
                        }
        }
        ```
