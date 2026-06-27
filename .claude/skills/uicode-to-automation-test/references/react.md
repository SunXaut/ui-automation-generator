# React 组件解析

## React 事件处理器映射

| React 事件 | Vue 指令 | Playwright 动作 |
|-----------|---------|---------------|
| `onClick` | `@click` | click |
| `onChange` | `@change` | fill |
| `onSubmit` | `@submit` | click (提交按钮) |
| `onBlur` | `@blur` | blur |
| `onFocus` | `@focus` | focus |
| `onDoubleClick` | `@dblclick` | dblclick |
| `onMouseEnter` | `@mouseenter` | hover |
| `onKeyDown` | `@keydown` | press |
| `onInput` | `@input` | fill |

## JSX 解析要点

1. **事件识别** — 匹配 `on<Event>` 模式（如 `onClick`, `onChange`）
2. **状态绑定** — 识别 `useState` hook 中的 `value` 和 `setXxx` 函数
3. **表单处理** — React 使用受控组件模式，`onChange` 更新状态
4. **Ref 绑定** — 识别 `useRef` 绑定的 `ref` 属性

## 选择器要点

- **data-testid** — 最可靠，适用于动态内容
- **aria-label** — 语义化，适合可访问性测试
- **getByRole** — 优先使用，但 React 渲染可能改变 DOM 结构
- **label 关联** — React 中 `<label htmlFor={id}>` 关联输入框

## Redux Reducer 测试

reducer 测试关注状态转换：

```typescript
expect(
  reducer(initialState, { type: 'LOGIN', payload: { username: 'test' } })
).toEqual({
  ...initialState,
  user: { username: 'test' },
  isAuthenticated: true
});
```

解析 reducer 函数，为每个 action type 生成状态转换测试用例。
