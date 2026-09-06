"""Telas completas de perfil e notificações embutidas na janela principal."""
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

def _clear(container):
    for child in container.winfo_children(): child.destroy()

def render_profile(container, root, user, api, theme, fonts, on_updated):
    _clear(container); title,body,small=fonts
    tk.Label(container,text="Meu perfil",font=title,bg=theme["bg"],fg=theme["text"]).pack(anchor="w",padx=30,pady=(28,4))
    status=tk.Label(container,text="Carregando…",font=small,bg=theme["bg"],fg=theme["text_dim"]); status.pack(anchor="w",padx=30)
    form=tk.Frame(container,bg=theme["surface"],padx=24,pady=20); form.pack(fill="x",padx=30,pady=18)
    fields={}
    for key,label in [("username","Usuário"),("display_name","Nome de exibição"),("email","E-mail")]:
        tk.Label(form,text=label,font=small,bg=theme["surface"],fg=theme["text_dim"]).pack(anchor="w",pady=(8,3))
        entry=tk.Entry(form,font=body,bg=theme["surface_alt"],fg=theme["text"],insertbackground=theme["text"],relief="flat")
        entry.pack(fill="x",ipady=8); fields[key]=entry
    fields["username"].config(state="disabled")
    role=tk.Label(form,text="",font=body,bg=theme["surface"],fg=theme["accent2"]); role.pack(anchor="w",pady=(14,4))
    def loaded(data,error=None):
        if error: status.config(text=error,fg=theme["accent2"]); return
        for key in fields:
            fields[key].config(state="normal"); fields[key].delete(0,"end"); fields[key].insert(0,data.get(key) or "")
        fields["username"].config(state="disabled"); role.config(text=f"Cargo: {data.get('role','user').title()}"); status.config(text="")
    def fetch():
        try: result=(api.get_profile(user.token),None)
        except Exception as exc: result=(None,str(exc))
        root.after(0,lambda:loaded(*result))
    threading.Thread(target=fetch,daemon=True).start()
    def save():
        status.config(text="Salvando…",fg=theme["text_dim"])
        def work():
            try: result=(api.update_profile(user.token,fields["display_name"].get().strip(),fields["email"].get().strip() or None),None)
            except Exception as exc: result=(None,str(exc))
            def done(data,error):
                if error: status.config(text=error,fg=theme["accent2"]); return
                status.config(text="Perfil atualizado.",fg=theme["read_badge_text"]); on_updated(data)
            root.after(0,lambda:done(*result))
        threading.Thread(target=work,daemon=True).start()
    tk.Button(form,text="Salvar alterações",command=save,bg=theme["accent"],fg="white",relief="flat",font=body,padx=18,pady=9).pack(anchor="e",pady=(18,0))
    security=tk.Frame(container,bg=theme["surface"],padx=24,pady=20); security.pack(fill="x",padx=30,pady=(0,18))
    tk.Label(security,text="Segurança",font=body,bg=theme["surface"],fg=theme["text"]).pack(anchor="w")
    old=tk.Entry(security,show="•",font=body,bg=theme["surface_alt"],fg=theme["text"],insertbackground=theme["text"],relief="flat")
    new=tk.Entry(security,show="•",font=body,bg=theme["surface_alt"],fg=theme["text"],insertbackground=theme["text"],relief="flat")
    for label,entry in [("Senha atual",old),("Nova senha",new)]:
        tk.Label(security,text=label,font=small,bg=theme["surface"],fg=theme["text_dim"]).pack(anchor="w",pady=(10,3)); entry.pack(fill="x",ipady=7)
    def change_password():
        if len(new.get())<8: messagebox.showerror("Segurança","A nova senha precisa ter ao menos 8 caracteres.",parent=root); return
        def work():
            try: api.change_password(user.token,old.get(),new.get()); error=None
            except Exception as exc: error=str(exc)
            root.after(0,lambda:messagebox.showerror("Segurança",error,parent=root) if error else messagebox.showinfo("Segurança","Senha alterada. Entre novamente no próximo acesso.",parent=root))
        threading.Thread(target=work,daemon=True).start()
    tk.Button(security,text="Trocar senha",command=change_password,bg=theme["accent"],fg="white",relief="flat",font=body,padx=18,pady=8).pack(anchor="e",pady=(14,0))
    if getattr(user,"role","user") in {"admin","owner"}:
        def enable_2fa():
            def work():
                try: setup,error=api.setup_2fa(user.token),None
                except Exception as exc: setup,error=None,str(exc)
                def show(setup,error):
                    if error: messagebox.showerror("2FA",error,parent=root);return
                    code=simpledialog.askstring("Ativar 2FA",f"Adicione este segredo ao autenticador:\n\n{setup['secret']}\n\nDigite o código gerado:",parent=root)
                    if not code:return
                    try: api.confirm_2fa(user.token,code);messagebox.showinfo("2FA","Autenticação em duas etapas ativada.",parent=root)
                    except Exception as exc: messagebox.showerror("2FA",str(exc),parent=root)
                root.after(0,lambda:show(setup,error))
            threading.Thread(target=work,daemon=True).start()
        tk.Button(security,text="Configurar autenticação em duas etapas",command=enable_2fa,bg=theme["surface_alt"],fg=theme["text"],relief="flat",font=small,padx=14,pady=8).pack(anchor="e",pady=(8,0))

def render_notifications(container, root, user, api, theme, fonts, on_count):
    _clear(container); title,body,small=fonts
    head=tk.Frame(container,bg=theme["bg"]); head.pack(fill="x",padx=30,pady=(28,10))
    tk.Label(head,text="Notificações",font=title,bg=theme["bg"],fg=theme["text"]).pack(side="left")
    status=tk.Label(container,text="Carregando…",font=small,bg=theme["bg"],fg=theme["text_dim"]); status.pack(anchor="w",padx=30)
    canvas=tk.Canvas(container,bg=theme["bg"],highlightthickness=0); canvas.pack(fill="both",expand=True,padx=30,pady=12)
    content=tk.Frame(canvas,bg=theme["bg"]); window=canvas.create_window((0,0),window=content,anchor="nw")
    canvas.bind("<Configure>",lambda e:canvas.itemconfig(window,width=e.width)); content.bind("<Configure>",lambda e:canvas.config(scrollregion=canvas.bbox("all")))
    def loaded(items,error=None):
        status.config(text=error or f"{sum(not x.get('read_at') for x in items)} não lida(s)",fg=theme["accent2"] if error else theme["text_dim"])
        if error:return
        on_count(sum(not x.get("read_at") for x in items))
        if not items: tk.Label(content,text="Nenhuma notificação.",font=body,bg=theme["bg"],fg=theme["text_dim"]).pack(pady=50); return
        for item in items:
            card=tk.Frame(content,bg=theme["surface_alt"] if not item.get("read_at") else theme["surface"],padx=16,pady=12)
            card.pack(fill="x",pady=5); tk.Label(card,text=item["title"],font=body,bg=card["bg"],fg=theme["text"]).pack(anchor="w")
            tk.Label(card,text=item["message"],font=small,bg=card["bg"],fg=theme["text_dim"],wraplength=760,justify="left").pack(anchor="w")
            if not item.get("read_at"): threading.Thread(target=lambda i=item:api.mark_notification_read(user.token,i["id"]),daemon=True).start()
        on_count(0)
    def fetch():
        try: result=(api.notifications(user.token),None)
        except Exception as exc: result=(None,str(exc))
        root.after(0,lambda:loaded(*result))
    threading.Thread(target=fetch,daemon=True).start()
