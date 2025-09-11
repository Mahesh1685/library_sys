**"Library Management System"**

*A complete web-based Library Management System built with Django featuring roll based access,adding books,librarian approval,and librarian tracking users and sending reports based on month wise.*

Features:-

1.Authentication ->     librarian with username and password,
                        student registers with email and create his password,
                        librarian approve student's request and sends an email which consists of students username(which will be students username)for logging in,
                        students as well as librarian can change his password by clicking forget password,
                        can logout after their job done

2.Student flow ->       register with email and year of study,
                        can request for borrowing books,
                        view issued(borrowed)books and return status such as due date ,fine amount after due date 
                        
2.Librarian flow ->     librarian can add books(books based on title,author,isbn code,total copies)
                        can edit books
                        can approve student for registered one
                        can approve books for borrow request [note:students only borrow those requested books physically)
                        can revoke the access of student
                        can also approve student to librarian 

        
                          
