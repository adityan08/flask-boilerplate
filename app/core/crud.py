from sqlalchemy.exc import IntegrityError

from app import db
from app.core.custom_errors import *
from app import logging


class CRUD:
    @classmethod
    def create(cls, model_is, data):
        try:
            record = model_is(**data)
            db.session.add(record)
        except Exception as e:
            logging.error(f"CRUD Create {model_is} {data} {e}")
            raise BadRequest(f"Please provide all fields correctly {e}")
        cls.db_commit()
        return record

    @classmethod
    def update(cls, model_is, condition, data):
        try:
            record = model_is.query.filter_by(**condition).update(data)
        except IntegrityError as e:
            db.session.rollback()
            print(e)
            logging.error(f"CRUD Update {model_is} {condition} {data} {e}")
            if 'errors.UniqueViolation' in str(e):
                raise UnProcessable("This data already exists")
            raise UnProcessable()
        if record:
            cls.db_commit()
            return True
        raise NoContent()

    @classmethod
    def create_if_not(cls, model_is, condition, data):
        record = model_is.query.filter_by(**condition).first()
        if not record:
            return cls.create(model_is, data)
        return record

    @classmethod
    def create_or_update(cls, model_is, condition, data):
        record = model_is.query.filter_by(**condition).first()
        if not record:
            return cls.create(model_is, data)
        return cls.update(model_is, condition, data)

    @classmethod
    def bulk_insertion(cls, model_is, data):
        for record in data:
            i = model_is(**record)
            db.session.add(i)
        cls.db_commit()

    @classmethod
    def delete(cls, model_is, condition):
        records = model_is.query.filter_by(**condition).all()
        try:
            for record in records:
                db.session.delete(record)
            cls.db_commit()
        except Exception as e:
            print(f"Crud delete exception {e} {condition} {model_is}")
        return True

    @staticmethod
    def db_commit():
        try:
            db.session.commit()
            return True
        except IntegrityError as e:
            print(e)
            logging.error(f"CRUD Commit {e}")
            db.session.rollback()
            if 'errors.UniqueViolation':
                try:
                    msg = str(e).split('Key (')[1].split(')')[0].replace(
                        '_', ' ').title() + ' already exists'
                except Exception as e:
                    msg = "This data already exists"
                raise UnProcessable(msg)
        except Exception as e:
            print(e)
            db.session.rollback()
            raise InternalError()
