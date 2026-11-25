# Lecture Notes reader

Static site (no build step). Drop this folder on Netlify. To test locally: `python3 -m http.server`, then open http://localhost:8000

## Files
- `index.html` – the reader (does not need editing to add content)
- `data/courses.json` – site title, footer, courses, languages, lesson list
- `data/<course>/NN-lesson.json` – one file per lesson
- `data/<course>/img/` – images (paths in JSON are relative to `data/`)

## courses.json
```
{ "title": "Lecture Notes",
  "footer": { "email": "...", "website": "https://..." },
  "courses": [
    { "id": "culture", "title": "Seminar on Culture Studies",
      "languages": [ {"code":"en","label":"EN","name":"English"},
                     {"code":"mn","label":"МН","name":"Монгол"} ],
      "lessons": [ {"id":"lewis-model","title":"The Lewis Model","file":"culture/05-lewis-model.json"} ] } ] }
```
- 1 to 5 languages per course; each language gets a column and a toggle button. `code` is the key used in the lesson blocks.
- Lessons appear in the sidebar in the order listed. `id` is used in the link (`#/culture/lewis-model`).

## Lesson file
`{"blocks":[ ... ]}` – each block is one row; its language versions sit side by side.

| `t` | meaning | value per language |
|---|---|---|
| `h2` `h3` `h4` | heading levels | string (`\n` = line break) |
| `p` | paragraph | string, or list of strings (several paragraphs in one row) |
| `li` | bullet | string, or list |
| `keys` | small tags | list of strings |
| `fig` | image, shown in every column | `"src"` and `"alt"` instead of language keys |

Inside a list, an item can be `{"t":"li","x":"..."}` to change its type, or `{"t":"a","x":"https://..."}` for a link.

Example:
`{"t":"p","en":"Hello.","mn":"Сайн байна уу."}`
`{"t":"fig","src":"culture/img/lewis.jpeg","alt":"The Lewis Model"}`
