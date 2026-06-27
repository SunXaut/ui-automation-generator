// AUTO-GENERATED START
import com.microsoft.playwright.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;
import java.pages.HomePage;

/**
 * Home 组件测试
 */
public class HomeTest {
    private Playwright playwright;
    private Browser browser;
    private Page page;
    private HomePage homePage;

    @BeforeEach
    public void setUp() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch();
        page = browser.newPage();
        homePage = new HomePage(page);
    }

    @AfterEach
    public void tearDown() {
        browser.close();
        playwright.close();
    }

    /**
     * 点击元素1
     */
    @Test
    public void testClickElement1() {
        homePage.goto();
        homePage.clickElement();
        // TODO: 添加断言
    }
}

// AUTO-GENERATED END