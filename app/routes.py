# app/routes.py - Routes and view functions for the app

import functools
from datetime import datetime, date, timedelta
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from app.db import get_db
from app.utils import calculate_bill

bp = Blueprint('app', __name__)


def login_required(view):
    """View decorator that redirects to the login page if user is not logged in."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('app.login'))
        return view(**kwargs)
    return wrapped_view


def role_required(roles):
    """View decorator that requires specific role(s)."""
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                return redirect(url_for('app.login'))
            
            if g.user['role'] not in roles:
                flash(f"Access denied. You need to be {' or '.join(roles)}.")
                if g.user['role'] == 'vehicle_owner':
                    return redirect(url_for('app.owner_dashboard'))
                else:
                    return redirect(url_for('app.management_dashboard'))
            
            return view(**kwargs)
        return wrapped_view
    return decorator


@bp.before_app_request
def load_logged_in_user():
    """Load user if logged in, and check if they're blocked."""
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        
        # Check if user is blocked
        if g.user and g.user['is_blocked'] == 1:
            session.clear()
            g.user = None
            flash('Your account has been blocked. Please contact management.')


@bp.route('/')
def index():
    """Redirect to appropriate dashboard based on user role or to login."""
    if g.user is None:
        return redirect(url_for('app.login'))
    
    if g.user['role'] == 'vehicle_owner':
        return redirect(url_for('app.owner_dashboard'))
    else:
        return redirect(url_for('app.management_dashboard'))


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if user is None:
            error = 'Incorrect username.'
        elif user['password'] != password:  # Plain text password as requested
            error = 'Incorrect password.'
        elif user['is_blocked'] == 1:
            error = 'Your account has been blocked. Please contact management.'
        
        if error is None:
            # Store the user ID in the session
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('app.index'))
        
        flash(error)
    
    return render_template('login.html')


@bp.route('/logout')
def logout():
    """Log out the current user."""
    session.clear()
    return redirect(url_for('app.login'))


@bp.route('/owner_dashboard', methods=('GET', 'POST'))
@login_required
@role_required(['vehicle_owner'])
def owner_dashboard():
    """Vehicle owner dashboard for logging usage and viewing history."""
    db = get_db()
    user_id = g.user['id']
    error = None
    today = date.today().isoformat()
    
    # Get user's default km setting
    default_setting = db.execute(
        'SELECT * FROM default_settings WHERE user_id = ? AND valid_until >= ?',
        (user_id, today)
    ).fetchone()
    
    # Check if setting exists and is still valid
    has_valid_default = default_setting is not None
    can_set_default = False
    days_until_change = 0
    
    if has_valid_default:
        # Calculate days until default can be changed
        valid_until = datetime.strptime(default_setting['valid_until'], '%Y-%m-%d').date()
        days_until_change = (valid_until - date.today()).days
    else:
        # User can set a new default
        can_set_default = True
    
    # Check if already logged usage for today
    today_log = db.execute(
        'SELECT * FROM usage_logs WHERE user_id = ? AND date = ?',
        (user_id, today)
    ).fetchone()
    
    already_logged_today = today_log is not None
    
    # Handle form submissions
    if request.method == 'POST':
        # Handle default km setting
        if 'set_default_km' in request.form and can_set_default:
            try:
                default_km = float(request.form['default_km'])
                
                # Simple validation
                if default_km <= 0 or default_km > 100:
                    error = 'Default KM must be between 0.1 and 100.'
                else:
                    # Calculate valid until date (30 days from today)
                    valid_until = (date.today() + timedelta(days=30)).isoformat()
                    
                    # Insert new default setting
                    db.execute(
                        'INSERT INTO default_settings (user_id, default_km, set_date, valid_until) '
                        'VALUES (?, ?, ?, ?)',
                        (user_id, default_km, today, valid_until)
                    )
                    db.commit()
                    flash('Monthly default KM set successfully! This value will be used for the next 30 days.')
                    return redirect(url_for('app.owner_dashboard'))
            except ValueError:
                error = 'Please enter a valid number for default KM.'
        
        # Handle extra km logging
        elif 'log_extra_km' in request.form and has_valid_default and not already_logged_today:
            try:
                extra_km = float(request.form['extra_km']) if request.form['extra_km'] else 0
                
                # Simple validation
                if extra_km < 0 or extra_km > 50:
                    error = 'Extra KM must be between 0 and 50.'
                else:
                    # Add to database using the stored default KM
                    db.execute(
                        'INSERT INTO usage_logs (user_id, date, default_km, extra_km) VALUES (?, ?, ?, ?)',
                        (user_id, today, default_setting['default_km'], extra_km)
                    )
                    db.commit()
                    flash('Daily usage recorded successfully!')
                    return redirect(url_for('app.owner_dashboard'))
            except ValueError:
                error = 'Please enter a valid number for extra KM.'
        
        if error:
            flash(error)
    
    # Get user's usage logs
    logs = db.execute(
        'SELECT * FROM usage_logs WHERE user_id = ? ORDER BY date DESC',
        (user_id,)
    ).fetchall()
    
    # Get user's bills
    bills = db.execute(
        'SELECT * FROM bills WHERE user_id = ? ORDER BY month DESC',
        (user_id,)
    ).fetchall()
    
    return render_template('owner_dashboard.html', 
                          logs=logs, 
                          bills=bills, 
                          default_setting=default_setting,
                          has_valid_default=has_valid_default,
                          can_set_default=can_set_default,
                          days_until_change=days_until_change,
                          already_logged_today=already_logged_today)


@bp.route('/management_dashboard')
@login_required
@role_required(['management'])
def management_dashboard():
    """Management dashboard for viewing users and their data."""
    db = get_db()
    
    # Get all vehicle owners
    vehicle_owners = db.execute(
        'SELECT * FROM users WHERE role = ?', ('vehicle_owner',)
    ).fetchall()
    
    # For each owner, get their usage data
    owners_data = []
    for owner in vehicle_owners:
        # Get default setting
        default_setting = db.execute(
            'SELECT * FROM default_settings WHERE user_id = ? AND valid_until >= ? ORDER BY set_date DESC LIMIT 1',
            (owner['id'], date.today().isoformat())
        ).fetchone()
        
        current_default = default_setting['default_km'] if default_setting else "Not set"
        
        # Get usage logs count
        logs_count = db.execute(
            'SELECT COUNT(*) as count FROM usage_logs WHERE user_id = ?',
            (owner['id'],)
        ).fetchone()['count']
        
        # Get total KM for current month
        current_month = datetime.now().strftime('%Y-%m')
        month_km = db.execute(
            'SELECT SUM(default_km) + SUM(extra_km) as total FROM usage_logs '
            'WHERE user_id = ? AND date LIKE ?',
            (owner['id'], f'{current_month}%')
        ).fetchone()
        total_km = month_km['total'] if month_km['total'] else 0
        
        # Check unpaid bills
        unpaid_bills = db.execute(
            'SELECT COUNT(*) as count FROM bills WHERE user_id = ? AND is_paid = 0',
            (owner['id'],)
        ).fetchone()['count']
        
        owners_data.append({
            'id': owner['id'],
            'username': owner['username'],
            'current_default': current_default,
            'is_blocked': owner['is_blocked'],
            'logs_count': logs_count,
            'current_month_km': total_km,
            'unpaid_bills': unpaid_bills,
            'payment_overdue': unpaid_bills >= 3
        })
    
    return render_template('management_dashboard.html', owners_data=owners_data)


@bp.route('/user/<int:user_id>/logs')
@login_required
@role_required(['management'])
def user_logs(user_id):
    """View all logs for a specific user."""
    db = get_db()
    
    # Get user info
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user is None:
        flash('User not found.')
        return redirect(url_for('app.management_dashboard'))
    
    # Get current default setting
    default_setting = db.execute(
        'SELECT * FROM default_settings WHERE user_id = ? AND valid_until >= ? ORDER BY set_date DESC LIMIT 1',
        (user_id, date.today().isoformat())
    ).fetchone()
    
    # Get logs
    logs = db.execute(
        'SELECT * FROM usage_logs WHERE user_id = ? ORDER BY date DESC',
        (user_id,)
    ).fetchall()
    
    # Get bills
    bills = db.execute(
        'SELECT * FROM bills WHERE user_id = ? ORDER BY month DESC',
        (user_id,)
    ).fetchall()
    
    # Get default history
    default_history = db.execute(
        'SELECT * FROM default_settings WHERE user_id = ? ORDER BY set_date DESC',
        (user_id,)
    ).fetchall()
    
    return render_template('user_logs.html', 
                           user=user, 
                           logs=logs, 
                           bills=bills, 
                           default_setting=default_setting,
                           default_history=default_history)


@bp.route('/toggle_block/<int:user_id>')
@login_required
@role_required(['management'])
def toggle_block(user_id):
    """Toggle the blocked status of a user."""
    db = get_db()
    
    # Get current status
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user is None:
        flash('User not found.')
        return redirect(url_for('app.management_dashboard'))
    
    # Toggle status
    new_status = 0 if user['is_blocked'] == 1 else 1
    db.execute(
        'UPDATE users SET is_blocked = ? WHERE id = ?',
        (new_status, user_id)
    )
    db.commit()
    
    action = "blocked" if new_status == 1 else "unblocked"
    flash(f'User {user["username"]} has been {action}.')
    return redirect(url_for('app.management_dashboard'))


@bp.route('/generate_bills')
@login_required
@role_required(['management'])
def generate_bills():
    """Generate monthly bills for all users based on their usage."""
    db = get_db()
    
    # Get all vehicle owners
    vehicle_owners = db.execute(
        'SELECT * FROM users WHERE role = ?', ('vehicle_owner',)
    ).fetchall()
    
    # Current month
    current_month = datetime.now().strftime('%Y-%m')
    
    # For each owner, generate a bill
    for owner in vehicle_owners:
        # Check if bill already exists for this month
        existing_bill = db.execute(
            'SELECT * FROM bills WHERE user_id = ? AND month = ?',
            (owner['id'], current_month)
        ).fetchone()
        
        if existing_bill is None:
            # Get month's usage
            month_usage = db.execute(
                'SELECT SUM(default_km) as default_total, SUM(extra_km) as extra_total '
                'FROM usage_logs WHERE user_id = ? AND date LIKE ?',
                (owner['id'], f'{current_month}%')
            ).fetchone()
            
            default_km = month_usage['default_total'] if month_usage['default_total'] else 0
            extra_km = month_usage['extra_total'] if month_usage['extra_total'] else 0
            
            # Calculate bill
            total_amount = calculate_bill(default_km, extra_km)
            
            # Add to database
            db.execute(
                'INSERT INTO bills (user_id, month, total_amount, is_paid) VALUES (?, ?, ?, 0)',
                (owner['id'], current_month, total_amount)
            )
    
    db.commit()
    flash('Monthly bills have been generated.')
    return redirect(url_for('app.management_dashboard'))