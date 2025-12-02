from routes.base import render

def load_web_routes(app):
    @app.route("/<language>/organizations/register", methods=["GET"])
    def org_register(language):
        return render("organization-register.html")
    
    @app.route("/<language>/organizations/register/save", methods=["POST"])
    def org_register_save(language):
        return render("organization-register.html")