// AUTO-GENERATED START
import com.microsoft.playwright.*;

/**
 * Login 页面对象模型
 * 封装页面元素定位器和操作方法
 */
public class LoginPage {
    private final Page page;

    public LoginPage(Page page) {
        this.page = page;
    }

    /**
     * 导航到页面
     */
    public void goto() {
        page.navigate("/login");
    }

    /**
     * 填写formData.username
     */
    public void fillformdata.username(String value) {
        page.getByLabel("formData.username").fill(value != null ? value : "test_value");
    }

    /**
     * 填写formData.password
     */
    public void fillformdata.password(String value) {
        page.getByLabel("formData.password").fill(value != null ? value : "test_value");
    }

    /**
     * 填写formData.rememberMe
     */
    public void fillformdata.rememberme(String value) {
        page.getByLabel("formData.rememberMe").fill(value != null ? value : "test_value");
    }
}

// AUTO-GENERATED END