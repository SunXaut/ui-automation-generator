// AUTO-GENERATED START
import com.microsoft.playwright.*;

/**
 * LoginForm 页面对象模型
 * 封装页面元素定位器和操作方法
 */
public class LoginFormPage {
    private final Page page;
    /** 用户名 元素定位器 */
    private final Locator usernameInput;
    /** 密码 元素定位器 */
    private final Locator passwordInput;
    /** 记住我 元素定位器 */
    private final Locator rememberMeInput;

    public LoginFormPage(Page page) {
        this.page = page;
        this.usernameInput = page.getByLabel("用户名");
        this.passwordInput = page.getByLabel("密码");
        this.rememberMeInput = page.getByLabel("记住我");
    }

    /**
     * 导航到页面
     */
    public void goto() {
        page.navigate("/loginform");
    }

    /**
     * Change用户名
     */
    public void clickUsernameInput() {
        this.usernameInput.click();
    }

    /**
     * Change密码
     */
    public void clickPasswordInput() {
        this.passwordInput.click();
    }

    /**
     * Change记住我
     */
    public void clickRememberMeInput() {
        this.rememberMeInput.click();
    }

    /**
     * 填写username
     */
    public void fillUsername(String value) {
        this.usernameInput.fill(value != null ? value : "test_value");
    }

    /**
     * 填写password
     */
    public void fillPassword(String value) {
        this.passwordInput.fill(value != null ? value : "test_value");
    }

    /**
     * 填写rememberMe
     */
    public void fillRememberMe(String value) {
        this.rememberMeInput.fill(value != null ? value : "test_value");
    }
}

// AUTO-GENERATED END