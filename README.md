# EV Charging Management System

A simple Flask web application for managing electric vehicle (EV) charging in apartment buildings. This system allows vehicle owners to log their daily usage and management to track and bill residents for their electricity usage.

## Features

### For Vehicle Owners
- Log daily EV charging usage (default kilometers and extra kilometers)
- View usage history
- View billing history

### For Management
- View all vehicle owners and their usage statistics
- Block/unblock vehicle owners
- Generate monthly bills
- View detailed logs and bills for each user

## Demo Accounts

- **Vehicle Owner**: username: `user1`, password: `password1`
- **Management**: username: `admin`, password: `adminpass`

## Project Structure

```
ev-charging-system/
├── app/
│   ├── __init__.py  # Flask application factory
│   ├── db.py        # Database connection helpers
│   ├── routes.py    # View functions and routes
│   └── utils.py     # Utility functions
├── templates/
│   ├── login.html
│   ├── owner_dashboard.html
│   ├── management_dashboard.html
│   └── user_logs.html
├── static/
│   └── style.css
├── instance/
│   └── database.db (auto-created)
├── schema.sql       # Database schema and sample data
├── run.py           # Application entry point
├── requirements.txt
└── README.md
```

## Features To Be Added in Future Versions

- Password hashing for security
- Email notifications for bills
- Payment integration
- Detailed analytics and reporting
- Admin user management
- Multi-language support

## Development Notes

This is a simplified version focusing on core functionality. In a production environment, additional security measures would be implemented, such as:
- Password hashing
- CSRF protection
- Input validation
- Role-based access control with proper middleware
- Error logging
