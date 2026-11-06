// Minimal dependency-free test harness.
#pragma once
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <string>
#include <vector>

namespace testing {
struct Case { std::string name; std::function<void()> fn; };
inline std::vector<Case>& Cases() { static std::vector<Case> c; return c; }
inline int& Failures() { static int f = 0; return f; }
struct Registrar { Registrar(const char* n, std::function<void()> f) { Cases().push_back({n, f}); } };
inline int RunAll() {
    int passed = 0;
    for (auto& c : Cases()) {
        int before = Failures();
        try { c.fn(); } catch (const std::exception& e) {
            std::printf("  EXCEPTION in %s: %s\n", c.name.c_str(), e.what());
            ++Failures();
        }
        bool ok = Failures() == before;
        std::printf("  [%s] %s\n", ok ? "ok" : "FAIL", c.name.c_str());
        if (ok) ++passed;
    }
    std::printf("%d/%zu passed\n", passed, Cases().size());
    return Failures() == 0 ? 0 : 1;
}
} // namespace testing

#define TEST(name) \
    static void name(); \
    static testing::Registrar reg_##name(#name, name); \
    static void name()

#define EXPECT_TRUE(cond) do { if (!(cond)) { \
    std::printf("    %s:%d: EXPECT_TRUE(%s) failed\n", __FILE__, __LINE__, #cond); ++testing::Failures(); } } while (0)
#define EXPECT_EQ(a, b) do { auto _a = (a); auto _b = (b); if (!(_a == _b)) { \
    std::printf("    %s:%d: EXPECT_EQ(%s, %s) failed\n", __FILE__, __LINE__, #a, #b); ++testing::Failures(); } } while (0)
#define EXPECT_THROWS(expr) do { bool _t = false; try { expr; } catch (...) { _t = true; } if (!_t) { \
    std::printf("    %s:%d: expected exception from %s\n", __FILE__, __LINE__, #expr); ++testing::Failures(); } } while (0)

#define TEST_MAIN() int main() { return testing::RunAll(); }
