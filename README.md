**"Library Management System"**

*A complete web-based Library Management System built with Django featuring roll based access,adding books,librarian approval,and librarian tracking users and sending reports based on month wise.*

![Django](https://img.shields.io/badge/Django-3.2%2B-red?logo=django)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Admin Panel](https://img.shields.io/badge/Admin%20Panel-Django-green)

Features:-

1.Authentication ->     librarian with username and password,  
                        student registers with email and create his password,  
                        librarian approve student's request and sends an email which consists of students username(which will be students username)for logging in,  
                        students as well as librarian can change his password by clicking forget password,  
                        can logout after their job done.
  
2.Student workflow ->   register with email and year of study,  
                        can request for borrowing books,  
                        view issued(borrowed)books and return status such as due date ,fine amount after due date .  
                          
2.Librarian workflow -> librarian can add books(books based on title,author,isbn code,total copies),  
                        can edit books,  
                        can approve student for registered one,  
                        can approve books for borrow request [note:students only borrow those requested books physically),  
                        can revoke the access of student,  
                        can also approve student to librarian,  
                        can delete books.  

3.Borrowing workflow -> after approval:-
                                        *copy count decreases
                                        *due date set (14 days)
                                        *record created in librarian dhasboard as well as student dashboard

4.Yearly scheduling -> cron job to promote students anually (1st year -> 2nd year // 2nd year -> 3rd year)
                       delete final year students on june 30 of every year(for 3rd years)
              
5.UI features -> used CSS and google fonts(poppins)
                  user friendly validation with show password toggle button
                  search functionality for books (for students/librarian) and students (for librarian)        
                          
6.Email integration -> approval confirmation for students
                       password reset emails
                       used gmail's SMTP


**Final Tech Stack**

Frontend -> HTML,CSS,JS
Backend -> Django
Database -> SQLite
Auth -> Built in Django + Custom Roles
Email -> GMAIL's SMTP 
Scheduling -> Django-crontab






*Developed by : R. Maheshwaran
College : Ramakrishna Mission Vivekananda College,Mylapore,Chennai-04*
