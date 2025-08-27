# Sistema de Controle de Estoque DistriFarma

**Descrição curta:**  
Aplicação Django de controle de estoque que permite cadastrar produtos, gerenciar entradas (compras), saídas (vendas) e acompanhar o saldo de estoque. Ideal como portfólio funcional e bem estruturado.

---

##  Tecnologias utilizadas
- **Python 3.x**  
- **Django**  
- **SQLite**  
- **Django REST Framework** (para APIs internas, se aplicável)  
- **Bootstrap / Tailwind / HTMX** 

---

##  Funcionalidades principais
- Cadastro de produtos com unidades de medida  
- Registro de compras e vendas com cálculo automático de total (quantidade × preço)  
- Atualização em tempo real do saldo de estoque após cada operação
- Consulta histórica de inventário com filtros por produto, data, etc.  
- (Opcional) API REST para integração com outros sistemas

---

##  Como executar localmente

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Unix/macOS
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Aplique migrações
python manage.py migrate

# Crie usuário admin (opcional)
python manage.py createsuperuser

# Rode o servidor de desenvolvimento
python manage.py runserver

# Acesse em: http://127.0.0.1:8000/
