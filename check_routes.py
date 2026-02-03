from app import create_app

app = create_app()
routes = [str(rule) for rule in app.url_map.iter_rules() if 'formal-lesson' in str(rule)]

print("=== Formal Lesson Routes ===")
for r in sorted(routes):
    print(r)

# Check specific route
if any('generate-improved' in r for r in routes):
    print("\n✅ generate-improved endpoint 已注册!")
else:
    print("\n❌ generate-improved endpoint 未找到!")
