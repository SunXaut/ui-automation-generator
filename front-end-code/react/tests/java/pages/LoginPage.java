// AUTO-GENERATED START
import com.microsoft.playwright.*;

/**
 * Login 页面对象模型
 * 封装页面元素定位器和操作方法
 */
public class LoginPage {
    private final Page page;
    /** setIsSubmitted(false)}>
            返回登录 元素定位器 */
    private final Locator setissubmittedfalsebackloginButton;

    public LoginPage(Page page) {
        this.page = page;
        this.setissubmittedfalsebackloginButton = page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("setIsSubmitted(false)}>
            返回登录"));
    }

    /**
     * 导航到页面
     */
    public void goto() {
        page.navigate("/login");
    }

    /**
     * ClicksetIsSubmitted(false)}>
            返回登录
     */
    public void clickSetissubmittedfalsebackloginButton() {
        this.setissubmittedfalsebackloginButton.click();
    }

    /**
     * 填写isSubmitted
     */
    public void fillIsSubmitted(String value) {
        page.getByLabel("isSubmitted").fill(value != null ? value : "test_value");
    }
}

// AUTO-GENERATED END