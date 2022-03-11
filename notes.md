
# api documentation
```
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```
# extra info
```
POST: to create data.
GET: to read data.
PUT: to update data.
DELETE: to delete data.
```
# keeping fork up to date
```
git checkout develop
git pull --rebase upstream develop
git push
```
# setup
creating a python venv to work in and install the project requirements
```
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```
# for admin purposes saving & upgrading
when you added some dependancies update the requirements
```
venv\Scripts\activate
call pip freeze > requirements.txt
```
when you want to upgrade the dependancies
```
venv\Scripts\activate
powershell "(Get-Content requirements.txt) | ForEach-Object { $_ -replace '==', '>=' } | Set-Content requirements.txt"
call pip install -r requirements.txt --upgrade
call pip freeze > requirements.txt
powershell "(Get-Content requirements.txt) | ForEach-Object { $_ -replace '>=', '==' } | Set-Content requirements.txt"
```
# branch cleanup
if your branch gets out of sync and for some reason you have many pushes and pulls, to become insync without pushing some random changes do this
```
git fetch origin
git reset --hard origin/{branchname}
git clean -f -d
```