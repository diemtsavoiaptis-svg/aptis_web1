@echo off
cd /d C:\Users\Admin\Desktop\aptis_web

echo ================================
echo PUSH CODE LEN GITHUB
echo ================================

git status

git add .
git commit -m "Update website"

git push

echo ================================
echo DA PUSH XONG LEN GITHUB
echo ================================
pause
