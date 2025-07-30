from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models.models import ParkingLot, ParkingSpot, User, Reservation, db, Admin

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')

@admin_blueprint.route('/dashboard')
@login_required
def dashboard():
    if not isinstance(current_user, Admin):
        flash("Access denied. Admin privileges required.")
        return redirect(url_for('user.dashboard'))
    lots = ParkingLot.query.all()
    users = User.query.all()
    reservations = Reservation.query.all()
    return render_template("admin_dashboard.html", lots=lots, users=users, reservations=reservations)

@admin_blueprint.route("/create_lot", methods=['GET', 'POST'])
@login_required
def create_parking_lot():
    if not isinstance(current_user, Admin):
        flash("Unauthorized.")
        return redirect(url_for('user.dashboard'))
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        pin = request.form['pin']
        price = float(request.form['price'])
        capacity = int(request.form['capacity'])
        lot = ParkingLot(name=name, address=address, pin_code=pin, price=price, capacity=capacity)
        db.session.add(lot)
        db.session.flush()  # get lot.id before commit
        for _ in range(capacity):
            db.session.add(ParkingSpot(lot_id=lot.id, status='A'))
        db.session.commit()
        flash("Parking lot created.")
        return redirect(url_for('admin.dashboard'))
    return render_template('create_parking_lot.html')

@admin_blueprint.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def edit_lot(lot_id):
    if not isinstance(current_user, Admin):
        flash("Admin privileges required.")
        return redirect(url_for('user.dashboard'))
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        lot.name = request.form['name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin']
        lot.price = float(request.form['price'])
        new_capacity = int(request.form['capacity'])
        old_capacity = lot.capacity

        if new_capacity > old_capacity:
            for _ in range(new_capacity - old_capacity):
                db.session.add(ParkingSpot(lot_id=lot.id, status='A'))
        elif new_capacity < old_capacity:
            available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').all()
            to_remove = old_capacity - new_capacity
            if len(available_spots) < to_remove:
                flash("Not enough available spots to remove! Vacate more spots first.")
                return redirect(url_for('admin.edit_lot', lot_id=lot.id))
            for spot in available_spots[:to_remove]:
                db.session.delete(spot)
        lot.capacity = new_capacity
        db.session.commit()
        flash("Parking Lot updated successfully.")
        return redirect(url_for('admin.dashboard'))
    return render_template('edit_parking_lot.html', lot=lot)

@admin_blueprint.route('/delete_lot/<int:lot_id>', methods=['POST'])
@login_required
def delete_lot(lot_id):
    if not isinstance(current_user, Admin):
        flash("Admin privileges required.")
        return redirect(url_for('user.dashboard'))
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
    if any(spot.status != 'A' for spot in spots):
        flash("Cannot delete lot. All spots must be vacant!")
        return redirect(url_for('admin.dashboard'))
    for spot in spots:
        db.session.delete(spot)
    db.session.delete(lot)
    db.session.commit()
    flash("Parking Lot deleted successfully.")
    return redirect(url_for('admin.dashboard'))
