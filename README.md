# MBTA Commuter Rail Departure Board

### Built With

* [Django](https://www.djangoproject.com/)
* [Bootstrap](https://getbootstrap.com)
* [JQuery](https://jquery.com)
* [Redis](https://redis.io/)
* [PostgreSQL](https://www.postgresql.org/)

## Getting Started


### Prerequisites

* Ubuntu
* python 3.8
  ```sh
  sudo apt-get update
  sudo apt-get install python
  ```
* pip
  ```sh
  sudo apt install python3-pip
  ```
### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/ivantm24/mbta_dashboard.git
   ```
2. Create virtual environment
   ```sh
   cd mbta_dashboard
   python3 -m venv venv
   ```
3. Install redis
   ```sh
   sudo apt install redis-server
   ```
4. Install postgresql
    ```sh
    sudo apt-get -y install postgresql
    ```
5. Create postgresql database 
    ```sh
    sudo -u postgres psql
    createdb mbta
    \q
    ```
    Note: the app asumes that the password for postgres user is password. To change this edit settings.py

6. Install dependecies in venv
    ```sh
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    ```
7. Run
    ```sh
    source venv/bin/activate
    python manage.py runserver
    ```
