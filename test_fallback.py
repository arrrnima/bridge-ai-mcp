from response_builder import build_response

for i in range(3):
    ans, rel = build_response(None, 0.0)
    print(ans)
    print("---")
