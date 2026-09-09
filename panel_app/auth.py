ROLE_LABELS={"user":"Usuário","moderator":"Moderador","admin":"Administrador","owner":"Dono"}
def role_label(user): return ROLE_LABELS.get(getattr(user,"role","user"),"Usuário")
