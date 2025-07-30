from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.models import ParkingLot, ParkingSpot, Reservation, db, User, Admin

user_blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_blueprint.route('/dashboard')
@login_required
def dashboard():
    # FIXED: Proper user check
    if isinstance(current_user, Admin):
        return redirect(url_for('admin.dashboard'))
    
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    lots = ParkingLot.query.all()
    return render_template("user_dashboard.html", reservations=reservations, lots=lots)

@user_blueprint.route('/reserve/<int:lot_id>')
@login_required
def reserve(lot_id):
    # FIXED: Ensure only regular users can reserve
    if isinstance(current_user, Admin):
        flash("Admins cannot make reservations.")
        return redirect(url_for('admin.dashboard'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    
    if not spot:
        flash("No spots available in selected lot!")
        return redirect(url_for('.dashboard'))
    
    # Reserve spot
    res = Reservation(user_id=current_user.id, spot_id=spot.id)
    spot.status = 'O'
    db.session.add(res)
    db.session.commit()
    
    flash(f"Reservation successful! Spot ID: {spot.id}")
    return redirect(url_for(".dashboard"))

@user_blueprint.route('/release/<int:reservation_id>')
@login_required
def release(reservation_id):
    # FIXED: Ensure only regular users can release
    if isinstance(current_user, Admin):
        flash("Admins cannot release reservations.")
        return redirect(url_for('admin.dashboard'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Ensure user can only release their own reservations
    if reservation.user_id != current_user.id:
        flash("You can only release your own reservations.")
        return redirect(url_for('.dashboard'))
    
    spot = ParkingSpot.query.get(reservation.spot_id)
    spot.status = 'A'
    reservation.leave()
    db.session.commit()
    
    flash("Spot released successfully.")
    return redirect(url_for('.dashboard'))
