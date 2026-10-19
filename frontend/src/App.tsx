import { useCallback, useEffect, useMemo, useState } from "react";
import { Activity, AlertCircle, ArrowDownUp, ArrowLeft, Bell, BookOpen, Check, ChevronLeft, ChevronRight, CircleHelp, Clock3, FilePlus2, FileText, Filter, LayoutDashboard, LogOut, Menu, Plus, RefreshCw, Search, Send, ShieldCheck, Ticket, UserRound, X } from "lucide-react";

type Category = { id:number; name:string; description:string|null };
type TicketItem = { id:number; title:string; description:string; category_id:number; category:string; status:string; priority:string; responsible_id:number|null; created_at:string; updated_at:string; deadline_at:string|null };
type Page = {items:TicketItem[]; total:number; limit:number; offset:number};
type CommentItem = {id:number;author_id:number;comment_text:string;is_internal:boolean;created_at:string};
type CurrentUser = {id:number;full_name:string;email:string;role:string};
const API = (import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1").replace(/\/$/, "");
const date = (value?:string|null) => value ? new Date(value).toLocaleDateString("ru-RU",{day:"2-digit",month:"short",year:"numeric"}) : "—";
const statusClass = (s:string) => /нов/i.test(s) ? "new" : /работ|process/i.test(s) ? "progress" : /реш|закры|done/i.test(s) ? "done" : "neutral";

export default function App() {
  const [token,setToken] = useState(() => sessionStorage.getItem("helpdesk_token") || "");
  const [email,setEmail] = useState("");
  const [currentUser,setCurrentUser] = useState<CurrentUser|null>(null);
  const [comments,setComments] = useState<CommentItem[]>([]);
  const [workflowStatus,setWorkflowStatus] = useState("Готово");
  const [workflowExplanation,setWorkflowExplanation] = useState("");
  const [workflowBusy,setWorkflowBusy] = useState(false);
  const [password,setPassword] = useState("");
  const [loginBusy,setLoginBusy] = useState(false);
  const [loginError,setLoginError] = useState("");
  const [page,setPage] = useState<Page|null>(null);
  const [categories,setCategories] = useState<Category[]>([]);
  const [loading,setLoading] = useState(false);
  const [error,setError] = useState("");
  const [query,setQuery] = useState("");
  const [statusFilter,setStatusFilter] = useState("Все статусы");
  const [offset,setOffset] = useState(0);
  const [active,setActive] = useState<"overview"|"requests">("overview");
  const [selected,setSelected] = useState<TicketItem|null>(null);
  const [modal,setModal] = useState<"create"|"edit"|null>(null);
  const [title,setTitle] = useState("");
  const [description,setDescription] = useState("");
  const [categoryId,setCategoryId] = useState("");
  const [saving,setSaving] = useState(false);
  const [formError,setFormError] = useState("");
  const [mobileMenu,setMobileMenu] = useState(false);
  const [notice,setNotice] = useState("");

  const api = useCallback(async (path:string, init:RequestInit = {}) => {
    const headers = new Headers(init.headers);
    headers.set("Content-Type","application/json");
    if (token) headers.set("Authorization", `Bearer ${token}`);
    const response = await fetch(`${API}${path}`,{...init,headers});
    if (response.status === 401 && token) {
      sessionStorage.removeItem("helpdesk_token"); setToken(""); throw new Error("Сессия завершена. Войдите снова.");
    }
    const body = response.status === 204 ? null : await response.json().catch(()=>null);
    if (!response.ok) throw new Error(body?.detail || `Ошибка запроса (${response.status})`);
    return body;
  },[token]);

  const load = useCallback(async (newOffset=offset) => {
    if (!token) return;
    setLoading(true); setError("");
    try {
      const [requests,cats,me] = await Promise.all([
        api(`/requests?limit=100&offset=${newOffset}`) as Promise<Page>,
        api("/categories") as Promise<Category[]>,
        api("/auth/me") as Promise<CurrentUser>
      ]);
      setPage(requests); setCategories(cats); setCurrentUser(me); setEmail(me.email);
    } catch(e) { setError(e instanceof Error ? e.message : "Не удалось загрузить данные"); }
    finally { setLoading(false); }
  },[api,token,offset]);
  useEffect(()=>{ if(token) void load(offset); },[token,offset,load]);

  const tickets = page?.items || [];
  const filtered = useMemo(()=>tickets.filter(t=>
    (statusFilter==="Все статусы" || t.status===statusFilter) &&
    ( `${t.id} ${t.title} ${t.category} ${t.description}`.toLowerCase().includes(query.toLowerCase()))
  ),[tickets,statusFilter,query]);
  const statuses = useMemo(()=>["Все статусы",...Array.from(new Set(tickets.map(t=>t.status)))],[tickets]);
  const openCreate = () => { setTitle("");setDescription("");setCategoryId(categories[0]?.id ? String(categories[0].id) : "");setFormError("");setModal("create"); };
  const openEdit = (t:TicketItem) => { setSelected(t);setTitle(t.title);setDescription(t.description);setFormError("");setModal("edit"); };
  const submitLogin = async (e:React.FormEvent) => {
    e.preventDefault();setLoginBusy(true);setLoginError("");
    try {
      const res = await fetch(`${API}/auth/login`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email,password})});
      const body = await res.json().catch(()=>null);
      if(!res.ok) throw new Error(body?.detail || "Неверный email или пароль");
      sessionStorage.setItem("helpdesk_token",body.access_token);setToken(body.access_token);setPassword("");
    } catch(e) {setLoginError(e instanceof Error ? e.message : "Не удалось войти");}
    finally {setLoginBusy(false);}
  };
  const submitTicket = async (e:React.FormEvent) => {
    e.preventDefault();setSaving(true);setFormError("");
    try {
      if(modal==="create") await api("/requests",{method:"POST",body:JSON.stringify({title,description,category_id:Number(categoryId)})});
      else if(selected) await api(`/requests/${selected.id}`,{method:"PATCH",body:JSON.stringify({title,description})});
      setModal(null);setNotice(modal==="create"?"Заявка создана":"Изменения сохранены");window.setTimeout(()=>setNotice(""),3200);await load(offset);
    } catch(e) {setFormError(e instanceof Error ? e.message : "Не удалось сохранить заявку");}
    finally {setSaving(false);}
  };
  const logout = () => {sessionStorage.removeItem("helpdesk_token");setToken("");setPage(null);setSelected(null);setCurrentUser(null);setComments([]);};
  const selectTicket = async (t:TicketItem) => {
    try {
      const [detail,history] = await Promise.all([
        api(`/requests/${t.id}`) as Promise<TicketItem>,
        api(`/requests/${t.id}/comments`) as Promise<CommentItem[]>
      ]);
      setSelected(detail); setComments(history); setWorkflowExplanation("");
    } catch(e) {setError(e instanceof Error?e.message:"Ошибка загрузки заявки");}
  };
  const updateWorkflow = async (e:React.FormEvent) => {
    e.preventDefault();
    if (!selected) return;
    setWorkflowBusy(true); setError("");
    try {
      const updated = await api(`/requests/${selected.id}/workflow`, {
        method:"PATCH", body:JSON.stringify({status:workflowStatus, explanation:workflowExplanation})
      }) as TicketItem;
      setSelected(updated); setWorkflowExplanation("");
      setNotice("Статус заявки обновлён"); window.setTimeout(()=>setNotice(""),3200);
      await load(offset);
      setComments(await api(`/requests/${updated.id}/comments`) as CommentItem[]);
    } catch(e) {setError(e instanceof Error?e.message:"Не удалось изменить статус");}
    finally {setWorkflowBusy(false);}
  };
  const isStaff = currentUser?.role === "Оператор" || currentUser?.role === "Администратор";
  const stats = [
    {label:"Всего заявок",value:page?.total ?? "—",icon:Ticket,style:"violet"},
    {label:"Новые",value:tickets.filter(t=>/нов/i.test(t.status)).length,icon:Clock3,style:"blue"},
    {label:"В работе",value:tickets.filter(t=>/работ|process/i.test(t.status)).length,icon:Activity,style:"amber"},
    {label:"Завершено",value:tickets.filter(t=>/реш|закры|done/i.test(t.status)).length,icon:Check,style:"green"}
  ];

  if(!token) return <div className="login-page"><div className="login-decoration"><div className="orb orb-one"/><div className="orb orb-two"/><div className="login-brand"><div className="brand-mark"><ShieldCheck size={26}/></div><span>SUSU <b>HelpDesk</b></span></div><div className="login-pitch"><span className="eyebrow">СЛУЖБА ПОДДЕРЖКИ</span><h1>Все обращения.<br/>В одном месте.</h1><p>Управляйте заявками, отслеживайте статус и оставайтесь на связи с командой поддержки.</p><div className="login-points"><span><Check size={16}/> Прозрачный статус обращений</span><span><Check size={16}/> История ваших заявок</span><span><Check size={16}/> Быстрое создание обращений</span></div></div><div className="login-foot">SUSU HelpDesk · Личный кабинет</div></div><div className="login-form-side"><form className="login-card" onSubmit={submitLogin}><div className="mobile-brand"><div className="brand-mark"><ShieldCheck size={24}/></div><span>SUSU <b>HelpDesk</b></span></div><span className="eyebrow">С ВОЗВРАЩЕНИЕМ</span><h2>Войти в аккаунт</h2><p className="muted">Введите данные вашей учётной записи</p>{loginError&&<div className="alert"><AlertCircle size={17}/>{loginError}</div>}<label>Email<input type="email" autoComplete="username" required value={email} onChange={e=>setEmail(e.target.value)} placeholder="name@susu.ru"/></label><label>Пароль<input type="password" autoComplete="current-password" required value={password} onChange={e=>setPassword(e.target.value)} placeholder="Введите пароль"/></label><button className="primary full" disabled={loginBusy}>{loginBusy?<RefreshCw className="spin" size={17}/>:<ShieldCheck size={17}/>} {loginBusy?"Входим…":"Войти в систему"}</button><div className="secure-note"><ShieldCheck size={15}/> Защищённое подключение к личному кабинету</div><div className="login-api">API: {API}</div></form></div></div>;

  return <div className="app-shell">
    <aside className={`sidebar ${mobileMenu?"show":""}`}><div className="side-brand"><div className="brand-mark"><ShieldCheck size={23}/></div><span>SUSU <b>HelpDesk</b></span><button className="icon-btn mobile-close" onClick={()=>setMobileMenu(false)}><X size={19}/></button></div><div className="side-caption">РАБОЧЕЕ ПРОСТРАНСТВО</div><button className={`nav-item ${active==="overview"?"active":""}`} onClick={()=>{setActive("overview");setSelected(null);setMobileMenu(false);}}><LayoutDashboard size={18}/> Обзор</button><button className={`nav-item ${active==="requests"?"active":""}`} onClick={()=>{setActive("requests");setSelected(null);setMobileMenu(false);}}><FileText size={18}/> {isStaff?"Все заявки":"Мои заявки"} <span className="nav-count">{page?.total??0}</span></button><div className="side-caption side-caption-bottom">ИНФОРМАЦИЯ</div><a className="nav-item" href={API.replace("/api/v1","")+"/docs"} target="_blank" rel="noreferrer"><BookOpen size={18}/> Документация API</a><a className="nav-item" href="mailto:support@susu.ru"><CircleHelp size={18}/> Поддержка</a><div className="sidebar-bottom"><div className="user-avatar"><UserRound size={19}/></div><div className="user-meta"><strong>{currentUser?.full_name||email||"Пользователь"}</strong><span>{currentUser?.role||"Личный кабинет"}</span></div><button className="icon-btn" title="Выйти" onClick={logout}><LogOut size={18}/></button></div></aside>
    {mobileMenu&&<button className="scrim" aria-label="Закрыть меню" onClick={()=>setMobileMenu(false)}/>}
    <main className="main-area"><header className="topbar"><button className="icon-btn menu-toggle" onClick={()=>setMobileMenu(true)}><Menu size={20}/></button><div className="breadcrumbs">Личный кабинет <ChevronRight size={14}/> <b>{selected? `Заявка #${selected.id}`:active==="overview"?"Обзор":"Мои заявки"}</b></div><div className="top-actions"><span className="connection"><span/> API подключён</span><button className="icon-btn" title="Обновить данные" onClick={()=>void load(offset)}><RefreshCw size={18}/></button><button className="icon-btn" title="Уведомления"><Bell size={18}/></button><div className="top-avatar"><UserRound size={17}/></div></div></header>
      <div className="content">
        {error&&<div className="alert page-alert"><AlertCircle size={17}/><span>{error}</span><button className="icon-btn" onClick={()=>setError("")}><X size={17}/></button></div>}
        {selected ? <><button className="back-link" onClick={()=>setSelected(null)}><ArrowLeft size={17}/> Все заявки</button><div className="page-heading detail-heading"><div><span className="eyebrow">ОБРАЩЕНИЕ №{selected.id}</span><h1>{selected.title}</h1><p className="muted">Создано {date(selected.created_at)} · Обновлено {date(selected.updated_at)}</p></div>{!isStaff&&selected.status==="Новая"&&<button className="primary" onClick={()=>openEdit(selected)}><FileText size={17}/> Редактировать</button>}</div><div className="detail-grid"><section className="panel detail-main"><div className="panel-title">Описание обращения</div><p className="description-text">{selected.description}</p><div className="detail-divider"/><div className="panel-title">Информация о заявке</div><div className="info-grid"><div><span>Категория</span><strong>{selected.category}</strong></div><div><span>Статус</span><strong><i className={`status-dot ${statusClass(selected.status)}`}/>{selected.status}</strong></div><div><span>Приоритет</span><strong>{selected.priority}</strong></div><div><span>Ответственный</span><strong>{selected.responsible_id??"Не назначен"}</strong></div><div><span>Срок выполнения</span><strong>{date(selected.deadline_at)}</strong></div><div><span>ID заявки</span><strong>#{selected.id}</strong></div></div></section><aside className="panel"><div className="panel-title">Хронология</div><div className="timeline"><div className="timeline-mark"><Check size={13}/></div><div><strong>Заявка создана</strong><span>{date(selected.created_at)}</span></div></div><div className="timeline"><div className="timeline-mark muted-mark"><Clock3 size={13}/></div><div><strong>Последнее изменение</strong><span>{date(selected.updated_at)}</span></div></div><div className="tip-box"><ShieldCheck size={18}/><span>{isStaff?"Изменения сохраняются в общей базе и видны заявителю.":"Статус и пояснения обновляются после обработки оператором."}</span></div></aside></div>
          <section className="panel" style={{marginTop:18}}>
            <div className="panel-title">История и пояснения</div>
            {comments.length===0?<p className="muted">Пояснений пока нет.</p>:comments.map(c=><div className="timeline" key={c.id}><div className="timeline-mark muted-mark"><FileText size={13}/></div><div><strong>{c.comment_text}</strong><span>{date(c.created_at)} · Пользователь #{c.author_id}</span></div></div>)}
          </section>
          {isStaff&&<section className="panel" style={{marginTop:18}}>
            <div className="panel-title">Обработка заявки</div>
            <form onSubmit={updateWorkflow} className="workflow-form">
              <label>Новый статус<select value={workflowStatus} onChange={e=>setWorkflowStatus(e.target.value)}><option>Готово</option><option>Отложена</option><option>В работе</option><option>Назначена</option><option>На проверке</option></select></label>
              <label>Пояснение заявителю<textarea required minLength={3} maxLength={5000} rows={3} value={workflowExplanation} onChange={e=>setWorkflowExplanation(e.target.value)} placeholder="Опишите выполненные действия или причину откладывания"/></label>
              <button className="primary" disabled={workflowBusy||workflowExplanation.trim().length<3}>{workflowBusy?<RefreshCw className="spin" size={17}/>:<Check size={17}/>} Сохранить статус и пояснение</button>
            </form>
          </section>}
        </> :
        <><div className="page-heading"><div><span className="eyebrow">ПАНЕЛЬ УПРАВЛЕНИЯ</span><h1>{active==="overview"?"Добро пожаловать!":isStaff?"Все заявки":"Мои заявки"}</h1><p className="muted">{isStaff?"Общий список заявок. Откройте обращение, чтобы изменить статус и добавить пояснение.":active==="overview"?"Следите за обращениями и быстро находите нужную информацию.":"Просматривайте обращения и управляйте новыми заявками."}</p></div><button className="primary" onClick={openCreate}><Plus size={18}/> Создать заявку</button></div>
        {active==="overview"&&<div className="stats-grid">{stats.map(s=><div className="stat-card" key={s.label}><div className={`stat-icon ${s.style}`}><s.icon size={20}/></div><div className="stat-label">{s.label}</div><div className="stat-bottom"><strong>{s.value}</strong><span className="stat-note">{s.label==="Всего заявок"?"За всё время":"В загруженном списке"}</span></div></div>)}</div>}
        <section className="panel requests-panel"><div className="requests-head"><div><h2>{active==="overview"?"Последние обращения":"Все обращения"}</h2><p className="muted">{page?.total??0} заявок в вашем аккаунте</p></div><button className="secondary" onClick={()=>{setActive("requests");void load(offset);}}><ArrowDownUp size={16}/> Все заявки</button></div><div className="table-tools"><div className="search-box"><Search size={17}/><input placeholder="Поиск по заявкам…" value={query} onChange={e=>setQuery(e.target.value)}/>{query&&<button className="icon-btn" onClick={()=>setQuery("")}><X size={15}/></button>}</div><div className="filter-box"><Filter size={16}/><select value={statusFilter} onChange={e=>setStatusFilter(e.target.value)}>{statuses.map(s=><option key={s}>{s}</option>)}</select></div></div>
        <div className="table-wrap"><table><thead><tr><th>Заявка</th><th>Категория</th><th>Статус</th><th>Приоритет</th><th>Создана</th><th></th></tr></thead><tbody>{loading&&tickets.length===0?<tr><td colSpan={6}><div className="table-state"><RefreshCw className="spin" size={21}/> Загружаем заявки…</div></td></tr>:filtered.length===0?<tr><td colSpan={6}><div className="table-state"><div className="empty-icon"><FileText size={24}/></div><strong>{query||statusFilter!=="Все статусы"?"Ничего не найдено":"Пока нет заявок"}</strong><span>{query||statusFilter!=="Все статусы"?"Попробуйте изменить параметры поиска.":"Создайте первую заявку, чтобы обратиться в поддержку."}</span>{!query&&statusFilter==="Все статусы"&&<button className="primary" onClick={openCreate}><Plus size={16}/> Создать заявку</button>}</div></td></tr>:filtered.slice(active==="overview"?0:undefined,active==="overview"?5:undefined).map(t=><tr key={t.id} onClick={()=>void selectTicket(t)}><td><div className="ticket-cell"><span className="ticket-icon"><FileText size={17}/></span><div><strong>{t.title}</strong><span>#{t.id} · Обновлено {date(t.updated_at)}</span></div></div></td><td><span className="category-label">{t.category}</span></td><td><span className={`status-pill ${statusClass(t.status)}`}><i/> {t.status}</span></td><td><span className="priority-label">{t.priority}</span></td><td>{date(t.created_at)}</td><td><button className="icon-btn row-arrow" title="Открыть заявку" onClick={e=>{e.stopPropagation();void selectTicket(t);}}><ChevronRight size={18}/></button></td></tr>)}</tbody></table></div><div className="table-footer"><span>Показано {filtered.length?Math.min(filtered.length,active==="overview"?5:filtered.length):0} из {page?.total??0}</span><div className="pagination"><button className="icon-btn" disabled={offset===0||loading} onClick={()=>setOffset(Math.max(0,offset-100))}><ChevronLeft size={17}/></button><span>Страница {Math.floor(offset/100)+1}</span><button className="icon-btn" disabled={!page||offset+page.limit>=page.total||loading} onClick={()=>setOffset(offset+100)}><ChevronRight size={17}/></button></div></div></section>
        <div className="bottom-note"><ShieldCheck size={17}/><span>Ваши обращения доступны только вам. Персональные данные защищены.</span><span className="bottom-spacer"/><button onClick={()=>void load(offset)}><RefreshCw size={14}/> Обновить</button></div></>}
      </div><footer className="footer"><span>© {new Date().getFullYear()} SUSU HelpDesk</span><span>Личный кабинет пользователя</span></footer>
    </main>
    {modal&&<div className="modal-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)setModal(null);}}><form className="modal-card" onSubmit={submitTicket}><div className="modal-head"><div><span className="eyebrow">{modal==="create"?"НОВОЕ ОБРАЩЕНИЕ":`ЗАЯВКА №${selected?.id}`}</span><h2>{modal==="create"?"Создать заявку":"Редактировать заявку"}</h2></div><button type="button" className="icon-btn" onClick={()=>setModal(null)}><X size={20}/></button></div><p className="muted">{modal==="create"?"Опишите проблему — команда поддержки получит ваше обращение.":"Изменять можно только заголовок и описание новой заявки."}</p>{formError&&<div className="alert"><AlertCircle size={17}/>{formError}</div>}<label>Заголовок <span className="required">*</span><input autoFocus required minLength={1} maxLength={200} value={title} onChange={e=>setTitle(e.target.value)} placeholder="Кратко опишите проблему"/></label>{modal==="create"&&<label>Категория <span className="required">*</span><select required value={categoryId} onChange={e=>setCategoryId(e.target.value)}><option value="" disabled>Выберите категорию</option>{categories.map(c=><option value={c.id} key={c.id}>{c.name}</option>)}</select>{categories.length===0&&<span className="field-hint">Категории не загружены. Обновите страницу или проверьте API.</span>}</label>}<label>Описание <span className="required">*</span><textarea required minLength={1} maxLength={10000} rows={5} value={description} onChange={e=>setDescription(e.target.value)} placeholder="Подробно опишите ситуацию, шаги воспроизведения и ожидаемый результат"/></label><div className="field-hint">{description.length}/10000 символов</div><div className="modal-actions"><button type="button" className="secondary" onClick={()=>setModal(null)}>Отмена</button><button className="primary" disabled={saving||(modal==="create"&&!categoryId)}>{saving?<RefreshCw className="spin" size={17}/>:modal==="create"?<Send size={17}/>:<Check size={17}/>} {saving?"Сохраняем…":modal==="create"?"Отправить заявку":"Сохранить изменения"}</button></div></form></div>}
    {notice&&<div className="toast"><Check size={18}/>{notice}<button className="icon-btn" onClick={()=>setNotice("")}><X size={16}/></button></div>}
  </div>;
}
