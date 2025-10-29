Service discovery here is an nginx proxy server,
and every service note-management,user-management,monitoring will be exposed through this.

now give me an overview on how the service-to-service communication between the below services should happen?
- note -(both ways) note : for authentication,authorization
- user,note - monitoring : to give the necessary log,trace,metrics


first scan the whole project, and point out if i miss anything and then give me the best way of communication between these services.