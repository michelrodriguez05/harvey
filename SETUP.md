# Harvey — Guía de configuración

## 1. Requisitos
- Python 3.11+
- Node.js 20+
- Una cuenta de Google (para Google Calendar)
- Una API key de Anthropic (Claude)

## 2. Backend (Python)

```bash
cd harvey
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y completa las variables:

```bash
cp .env.example .env
```

### Variables requeridas en `.env`

| Variable | Cómo obtenerla |
|---|---|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `GOOGLE_CLIENT_ID` | Google Cloud Console → Credenciales → OAuth 2.0 |
| `GOOGLE_CLIENT_SECRET` | Mismo lugar |

### Configurar Google Cloud Console
1. Ve a https://console.cloud.google.com
2. Crea un proyecto nuevo (o usa uno existente)
3. Habilita la **Google Calendar API**
4. Ve a **Credenciales** → **Crear credenciales** → **ID de cliente OAuth 2.0**
5. Tipo: **Aplicación web**
6. Agrega `http://localhost:8000/auth/google/callback` a los URIs de redireccionamiento
7. Copia el Client ID y Client Secret al `.env`

### Iniciar el backend
```bash
uvicorn backend.main:app --reload
```

## 3. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

## 4. Conectar Google Calendar

1. Abre http://localhost:5173
2. Haz clic en el ícono de cuadrícula (Agenda) en el header
3. Verás el aviso "Google Calendar no conectado" → haz clic en **Conectar**
4. Autoriza el acceso con tu cuenta de Google

¡Listo! Harvey podrá:
- Agendar eventos diciendo *"Agéndame una reunión el viernes a las 3pm"*
- Consultar tu semana *"¿Qué tengo esta semana?"*
- Agregar tareas *"Recuérdame comprar leche, prioridad alta"*
- Guardar notas *"Guarda esto: contraseña del wifi es 12345"*

## Uso por voz
- Mantén pulsado el botón del micrófono → habla → suéltalo
- Harvey escucha, entiende y responde en voz y texto

## Uso por texto
- Escribe en el campo de texto y pulsa Enter o el botón enviar
