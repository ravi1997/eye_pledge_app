from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # ------------------------
    # Database model
    # ------------------------
    class EyeDonationPledge(db.Model):
        __tablename__ = "eye_donation_pledges"

        id = db.Column(db.Integer, primary_key=True)

        # Donor information
        donor_name = db.Column(db.String(200), nullable=False)
        relation = db.Column(db.String(50))  # son / daughter / wife of
        relative_name = db.Column(db.String(200))
        age = db.Column(db.Integer)
        address = db.Column(db.Text)

        place = db.Column(db.String(100))
        date_of_pledge = db.Column(db.Date)
        time_of_pledge = db.Column(db.Time)

        # Witness 1 (Next of kin)
        witness1_name = db.Column(db.String(200))
        witness1_relationship = db.Column(db.String(100))
        witness1_address = db.Column(db.Text)
        witness1_telephone = db.Column(db.String(50))
        witness1_mobile = db.Column(db.String(50))

        # Witness 2
        witness2_name = db.Column(db.String(200))
        witness2_address = db.Column(db.Text)
        witness2_telephone = db.Column(db.String(50))
        witness2_mobile = db.Column(db.String(50))

        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Make model importable as app.EyeDonationPledge
    app.EyeDonationPledge = EyeDonationPledge

    # ------------------------
    # Routes
    # ------------------------
    @app.route("/", methods=["GET", "POST"])
    def pledge_form():
        if request.method == "POST":
            try:
                # Parse date & time
                date_str = request.form.get("date_of_pledge") or None
                time_str = request.form.get("time_of_pledge") or None

                date_obj = (
                    datetime.strptime(date_str, "%Y-%m-%d").date()
                    if date_str
                    else None
                )
                time_obj = (
                    datetime.strptime(time_str, "%H:%M").time()
                    if time_str
                    else None
                )

                pledge = EyeDonationPledge(
                    donor_name=request.form.get("donor_name"),
                    relation=request.form.get("relation"),
                    relative_name=request.form.get("relative_name"),
                    age=(
                        int(request.form.get("age"))
                        if request.form.get("age")
                        else None
                    ),
                    address=request.form.get("address"),
                    place=request.form.get("place"),
                    date_of_pledge=date_obj,
                    time_of_pledge=time_obj,
                    witness1_name=request.form.get("witness1_name"),
                    witness1_relationship=request.form.get(
                        "witness1_relationship"
                    ),
                    witness1_address=request.form.get("witness1_address"),
                    witness1_telephone=request.form.get("witness1_telephone"),
                    witness1_mobile=request.form.get("witness1_mobile"),
                    witness2_name=request.form.get("witness2_name"),
                    witness2_address=request.form.get("witness2_address"),
                    witness2_telephone=request.form.get("witness2_telephone"),
                    witness2_mobile=request.form.get("witness2_mobile"),
                )

                db.session.add(pledge)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f"Error saving form: {e}", "danger")
                return render_template("pledge_form.html")

            return redirect(url_for("success"))

        # GET
        return render_template("pledge_form.html")

    @app.route("/success")
    def success():
        return render_template("success.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
