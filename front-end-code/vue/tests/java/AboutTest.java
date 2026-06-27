// AUTO-GENERATED START
import com.microsoft.playwright.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;
import java.pages.AboutPage;

/**
 * About 组件测试
 */
public class AboutTest {
    private Playwright playwright;
    private Browser browser;
    private Page page;
    private AboutPage aboutPage;

    @BeforeEach
    public void setUp() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch();
        page = browser.newPage();
        aboutPage = new AboutPage(page);
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
        aboutPage.goto();
        aboutPage.clickElement();
        // TODO: 添加断言
    }
}

// AUTO-GENERATED END