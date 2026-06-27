// AUTO-GENERATED START
import com.microsoft.playwright.*;

/**
 * Dashboard 页面对象模型
 * 封装页面元素定位器和操作方法
 */
public class DashboardPage {
    private final Page page;

    public DashboardPage(Page page) {
        this.page = page;
    }

    /**
     * 导航到页面
     */
    public void goto() {
        page.navigate("/dashboard");
    }

    /**
     * 填写count
     */
    public void fillCount(String value) {
        page.getByLabel("count").fill(value != null ? value : "test_value");
    }
}

// AUTO-GENERATED END