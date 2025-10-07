from sessionarchitect import create_app

app = create_app()

if __name__ == '__main__':
    # This command creates all the tables in your database file (site.db)
    with app.app_context():
        from sessionarchitect import db
        db.create_all()
        
    app.run(debug=True)