### Requirements
- [Docker](https://www.docker.com/)

### Requirements (Dev)
- Python ^3.11 
- [Poetry](https://python-poetry.org/)
 

### How to run?

Clone repo
```bash
git clone https://github.com/va1ker/flask-test-task.git
```

Enter the project folder with

```bash
cd flask-test-task
```

Start app with

```bash
docker compose up
```

### How to test?

Simply send POST requests with args to endpoint like this

I recommend use Postman for this
```
http://127.0.0.1:5000/update_user?user_id=2&city=moscow
```

https://docs.google.com/document/d/1jQdUgI4kEiZ14B7vQAt0Ioaqspub1zhakej3rqXi6Zc/edit