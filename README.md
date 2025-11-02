# PeoplePad MVP — Product & Engineering Spec

## Overview
PeoplePad is a lightweight personal knowledge app for remembering people you meet.  
The MVP is designed for private use (local deployment, a few users).

### Setup and run
- `docker compose up --build`
- Run migrations `docker compose exec backend alembic upgrade head`

---
Generate working runnable code, no stubs, no omissions
- Google OAuth login (any Google account can log in).  
- Each user only sees their own records.   

- Tech: TypeScript, Vite, React Router v6, react-query, react-hook-form, shadcn/ui, custom Tailwind theme
- don't over-fragment routes. Lazy load entire “record” routes (add/edit/view) as one chunk.
- this is MVP, do not use zod
- set up for local dev first with vite `npm run dev`
- keep routes flat (/dashboard, /add, /view/:id, /edit/:id). Don’t over-engineer nested layouts yet.
- Make sure you refetch tags when new records are added/edited (react-query’s invalidateQueries(['tags']) solves this).
- Extract a <RecordForm /> used in both Add + Edit → prevents duplication.
- Extract <SearchPanel /> with its own state and form handling.
- API Layer
- Wrap all fetches in a small /lib/api.ts with typed methods (getRecords, addRecord, etc.), so your react-query hooks are thin.
- remember that toaster is deprecated in shadcn, use sonner or whatever is applicable
- all needed shadcn components are copied, don't generate their code

#### Login Flow
When a user clicks login button
- open google auth URL in another tab 
When the login is done
- backend processes the callback in the popup (done in backend)
- sends the tokens back to the main window via postMessage (done in backend)
- closes the popup (done in backend)
- and the main app saves the tokens

#### Dashboard
- renders the header
- the search pane
- do not do an empty string search
---
### API
#### Schemas

```
class RecordCreate(BaseModel):
    name: str
    notes: Optional[str] = None
    tags: List[str] = []

class RecordUpdate(BaseModel):
    name: str
    notes: Optional[str] = None
    tags: List[str] = []

class RecordResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    notes: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

class SearchRequest(BaseModel):
    query: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: List[str] = []

class SearchResponse(BaseModel):
    id: UUID
    name: str
    notes: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    distance: float
    
class TagResponse(BaseModel):
    id: UUID
    name: str
```

#### Examples
```
# Example Request (POST /records):
# {
#   "name": "John Doe",
#   "notes": "Met at conference, works in AI",
#   "tags": ["conference", "AI"]
# }
#
# Example Response:
# {
#   "id": "123e4567-e89b-12d3-a456-426614174000",
#   "user_id": "456e7890-e12b-34d5-a678-426614174000",
#   "name": "John Doe",
#   "notes": "Met at conference, works in AI",
#   "tags": ["conference", "AI"],
#   "created_at": "2025-09-25T14:17:00Z",
#   "updated_at": "2025-09-25T14:17:00Z"
# }

# Example Request (POST /search):
# {
#   "query": "AI conference",
#   "start_date": "2025-01-01T00:00:00Z",
#   "end_date": "2025-12-31T23:59:59Z",
#   "tags": ["conference", "AI"]
# }
#
# Example Response:
# [
#   {
#     "id": "123e4567-e89b-12d3-a456-426614174000",
#     "name": "John Doe",
#     "notes": "Met at conference, works in AI",
#     "created_at": "2025-09-25T14:17:00Z",
#     "updated_at": "2025-09-25T14:17:00Z",
#     "distance": 0.123
#   }
# ]
```

---
Wireframes
1. Landing/Login
```
+----------------------------------------+
|                                        |
|               PeoplePad                |
|                                        |
|        [ Sign in with Google ]         |
|                                        |
+----------------------------------------+
```
2. Dashboard
```
+------------------------------------------------------------+
| PeoplePad                        + Add Record   [Avatar ▼] |
+------------------------------------------------------------+

Search:
[ Search text input..................... ] [ Tag filter ▼ ] 
[ From date ] to [ To date ]  [ Search ]

--------------------------------------------------------------
Results (ranked by similarity):

1. John Doe     | Notes: Met at conference, works at Acme... 
   Tags: [sales] [toronto]   Last Modified: Sep 20, 2025

2. Jane Smith   | Notes: Designer, UX background in fintech...
   Tags: [design]             Last Modified: Sep 15, 2025
--------------------------------------------------------------
```
3. Add record;
```
+------------------------------------------------------------+
| < Back                                                     |
+------------------------------------------------------------+

Add Record
--------------------------------------------------------------
Name: [....................]

Notes:
[ Multiline text area................................. ]

Tags: [ Type here to add... ]  (suggest dropdown appears)
      [ ux ] [ conference ]

--------------------------------------------------------------
[ Save ]   [ Cancel ]
```
4. View Record
```
+------------------------------------------------------------+
| < Back to Search                 [ Edit Record ]           |
+------------------------------------------------------------+

John Doe
--------------------------------------------------------------
Notes:
Met at conference, works at Acme on sales strategy...

Tags:
[ sales ] [ toronto ]

Created: Sep 1, 2025    Modified: Sep 20, 2025
```
5. Edit record:
```
+------------------------------------------------------------+
| < Back                                                     |
+------------------------------------------------------------+

Edit Record
--------------------------------------------------------------
Name: [ John Doe ]

Notes:
[ Met at conference, works at Acme on sales strategy... ]

Tags: [ sales ] [ toronto ]

--------------------------------------------------------------
[ Save ]   [ Cancel ]
```
---
## Minimal Style Guide

    Typography:

        Headings → Inter or Roboto (Sans-serif, clean, modern)

        Body → Inter or Roboto

    Colors (light theme MVP):

        Background → #FFFFFF

        Header / Primary → #2563EB (blue-600)

        Buttons → Filled primary (#2563EB), text white

        Secondary buttons → Gray border #D1D5DB

        Tags → Rounded pills, light background (#EFF6FF for blue, #F3F4F6 neutral)

        Text → #111827 (almost black), Subtext #6B7280 (gray)

    Spacing: 16px base grid, clean whitespace.

    Form controls: Rounded corners (4–6px).
---
## Rough folder structure - feel free to make changes
peoplepad-frontend/
├── public/
│   └── favicon.ico                 # Logo/branding assets
│
├── src/
│   ├── app/                        # App-wide providers, routing, layout
│   │   ├── App.tsx                 # Root component, wraps Router + Providers
│   │   ├── routes.tsx              # React Router v6 routes (lazy-loaded)
│   │   ├── providers/              
│   │   │   ├── AuthProvider.tsx    # Context for Google OAuth user
│   │   │   ├── QueryProvider.tsx   # React Query + Devtools setup
│   │   │   └── ToastProvider.tsx   # shadcn/ui toast wrapper
│   │   └── layout/                 
│   │       ├── Header.tsx          # Logo, Add button, Avatar menu
│   │       └── MainLayout.tsx      # Shared page layout
│   │
│   ├── features/                   # Feature-based organization
│   │   ├── auth/
│   │   │   ├── LandingPage.tsx     # Sign in with Google
│   │   │   └── useAuth.ts          # Hook to access auth context
│   │   │
│   │   ├── records/
│   │   │   ├── DashboardPage.tsx   # Search panel + results
│   │   │   ├── AddRecordPage.tsx   # Add record form
│   │   │   ├── EditRecordPage.tsx  # Edit record form
│   │   │   ├── ViewRecordPage.tsx  # Full record view
│   │   │   ├── components/         
│   │   │   │   ├── RecordForm.tsx  # Shared Add/Edit form
│   │   │   │   ├── SearchPanel.tsx # Search inputs
│   │   │   │   ├── RecordList.tsx  # Results list
│   │   │   │   └── RecordItem.tsx  # Single record row
│   │   │   └── hooks/
│   │   │       ├── useRecords.ts   # react-query hooks (list, add, edit)
│   │   │       └── useTags.ts      # react-query hook for tags
│   │   │
│   │   └── tags/
│   │       ├── TagAutocomplete.tsx # Notion-style prefix search
│   │       └── TagChip.tsx         # Tag pill (Badge wrapper)
│   │
│   ├── components/ui/              # shadcn/ui local copies
│   │
│   ├── lib/                        # API + schemas + utils
│   │   ├── api.ts                  # Fetch wrappers (getRecords, addRecord…)
│   │
│   ├── hooks/                      # App-level reusable hooks
│   │   └── useToast.ts             # or any other way to use Sonner from Shadcn
│   │
│   ├── tests/                      # Centralized test helpers
│   │   └── setup.ts                # Vitest + RTL setup (mocks, providers)
│   │
│   ├── index.css                   # Tailwind base + custom colors
│   ├── main.tsx                    # Vite entry point
│   └── vite-env.d.ts               # TypeScript vite env typings
│
├── tailwind.config.js              # Tailwind config (with custom palette)
├── tsconfig.json                   # TypeScript config
├── vite.config.ts                  # Vite config
├── package.json
└── README.md


