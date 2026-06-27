// AUTO-GENERATED START
import com.microsoft.playwright.Page;
import pages.LoginFormPage;

/**
 * 登录流程
 * 组合POM操作：goto → fillUsername → fillPassword → clickLoginButton
 */
public class LoginFormLoginBAW {
    private final LoginFormPage loginFormPage;

    public LoginFormLoginBAW(Page page) {
        this.loginFormPage = new LoginFormPage(page);
    }

    /**
     * 执行登录流程
     */
    public void execute(String username, String password) {
        // 1. goto
        loginFormPage.goto();
        // 2. fillUsername
        loginFormPage.fillUsername(username);
        // 3. fillPassword
        loginFormPage.fillPassword(password);
        // 4. clickLoginButton
        loginFormPage.clickLoginButton();
    }
}

// AUTO-GENERATED END