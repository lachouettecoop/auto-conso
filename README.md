# Auto-Conso
Client web pour enregistrer les pertes et auto consommations

### Requirement
You will need :
- docker
- docker-compose

### Build

```bash
docker-compose build
```

### Run
auto-conso docker needs some environment variables defined in file api.env.
```bash
JWT_SECRET=...                    # Secret for JSON Web Tokens signature
LDAP_ADMIN_PASS=...               # LDAP admin password

ODOO_URL=https://odoo.fr          # Odoo jsonrc URL
ODOO_LOGIN=...                    # Odoo user login
ODOO_PASSWORD=...                 # Odoo user password
ONLY_USERS=...                    # Authorized short list users

ALLOW_ALL_ORIGINS=...             # For development
```
Then run
```bash
docker-compose up -d
```

API will be accessible to http://localhost:8080/api/ping
```bash
curl http://localhost:8080/api/ping
```
It shall respond `{"name":"auto-conso","status":"ok"}`

### Development
```bash
poetry install
poetry run python main.py

cd ./client
npm run build
npm run serve
```
