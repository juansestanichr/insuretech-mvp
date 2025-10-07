from ..storage import SessionLocal, Customer as DBCustomer

class Customer360Agent:
    def upsert(self, customer_id: str, name: str, email: str, phone: str | None = None):
        with SessionLocal() as s:
            db = s.query(DBCustomer).filter_by(customer_id=customer_id).one_or_none()
            if not db:
                db = DBCustomer(customer_id=customer_id, name=name, email=email, phone=phone)
                s.add(db)
            else:
                db.name, db.email, db.phone = name, email, phone
            s.commit()
        return True

    def get(self, customer_id: str):
        with SessionLocal() as s:
            db = s.query(DBCustomer).filter_by(customer_id=customer_id).one_or_none()
            if not db:
                return None
            return {"customer_id": db.customer_id, "name": db.name, "email": db.email, "phone": db.phone}
