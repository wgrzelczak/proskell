@startuml
skinparam ConditionEndStyle hline
start
:Inicjalizacja;
repeat :Oczekuj na zgłoszenie;
 :Nowe zgłoszenie;
 :Walidacja danych wejściowych;
  if (Poprawne dane wejściowe?) then (Tak)
   :<b>Uruchom Robotnika\nSkompiluj program;
   if (Poprawna kompilacja?) then (Tak)
    while (Dostępne przypadki testowe?) is (Tak)
     :<b>Uruchom Robotnika\nUruchom program dla kolejnego testu;
    endwhile (Nie)
   else (Nie)
   -[dotted]->Nie;
   endif
  else (Nie)
  -[dotted]->Nie;
  endif

  :Wyślij odpowiedź;
repeatwhile
@enduml