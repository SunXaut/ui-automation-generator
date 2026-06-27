// AUTO-GENERATED START
import com.microsoft.playwright.Page;
import pages.LoginPage;

/**
 * 登录流程
 * 组合POM操作：goto → fillUsername → fillPassword → clickLoginButton
 */
public class LoginLoginBAW {
    private final LoginPage loginPage;

    public LoginLoginBAW(Page page) {
        this.loginPage = new LoginPage(page);
    }

    /**
     * 执行登录流程
     */
    public void execute(String username, String password) {
        // 1. goto
        loginPage.goto();
        // 2. fillUsername
        loginPage.fillUsername(username);
        // 3. fillPassword
        loginPage.fillPassword(password);
        // 4. clickLoginButton
        loginPage.clickLoginButton();
    }
}

// AUTO-GENERATED END