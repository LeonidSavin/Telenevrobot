@echo off
setlocal EnableDelayedExpansion
@chcp 65001

echo.>> log.txt
echo  !DATE!  %time:~1,7% Запуск бота...
echo  !DATE!  %time:~1,7% Бот запущен >> log.txt
START /WAIT "%~dp0" "experiment_03.py" >> log.txt 2>&1
for /l %%i in (1,1,100) do (
	echo  !DATE!  %time:~1,7% бот прекратил работу. Ожидание перезапуска...
	echo  !DATE!  %time:~1,7% бот прекратил работу >> log.txt
	if %%i% gtr 50 echo слишком много сбоев. Проверьте сетевое соединение! 
	timeout /t 15
	echo  !DATE!  %time:~1,7% Перезапуск номер %%i
	echo  !DATE!  %time:~1,7% Перезапуск номер %%i >> log.txt
	START /WAIT "%~dp0" "experiment_03.py" >> log.txt 
)
echo !DATE!  !TIME! Бот был перезапущен 100 раз. Завершение работы... 
echo !DATE!  !TIME! Бот был перезапущен 100 раз. Завершение работы >> log.txt
endlocal
