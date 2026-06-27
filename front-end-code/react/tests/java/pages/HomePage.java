// AUTO-GENERATED START
import com.microsoft.playwright.*;

/**
 * Home 页面对象模型
 * 封装页面元素定位器和操作方法
 */
public class HomePage {
    private final Page page;

    public HomePage(Page page) {
        this.page = page;
    }

    /**
     * 导航到页面
     */
    public void goto() {
        page.navigate("/home");
    }

    /**
     * 填写message
     */
    public void fillMessage(String value) {
        page.getByLabel("message").fill(value != null ? value : "test_value");
    }
}

// AUTO-GENERATED END