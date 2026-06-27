// AUTO-GENERATED START
import com.microsoft.playwright.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;
import java.pages.LoginPage;

/**
 * Login 组件测试
 */
public class LoginTest {
    private Playwright playwright;
    private Browser browser;
    private Page page;
    private LoginPage loginPage;

    @BeforeEach
    public void setUp() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch();
        page = browser.newPage();
        loginPage = new LoginPage(page);
    }

    @AfterEach
    public void tearDown() {
        browser.close();
        playwright.close();
    }

    /**
     * ClicksetIsSubmitted(false)}>
            返回登录
     */
    @Test
    public void testClickSetissubmittedfalsebacklogin() {
        loginPage.goto();
        loginPage.clickSetissubmittedfalsebackloginButton();
        // TODO: 添加断言
    }

    /**
     * Login)}
     */
    @Test
    public void testClickElement() {
        loginPage.goto();
        loginPage.clickElement();
        // TODO: 添加断言
    }
}

// AUTO-GENERATED END