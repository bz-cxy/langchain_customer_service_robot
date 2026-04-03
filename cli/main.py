from langchain_customer_service_robot.bot.customer_service_bot import CustomerServiceBot


def main():
    """命令行入口"""
    bot = CustomerServiceBot()
    
    print("-" * 50)
    print("> 智能客服机器人")
    print("-" * 50)
    
    print("\n请输入您的客户ID（如user001）")
    user_id = input("客户ID： ").strip() or "user001"
    
    sessions = bot.storage.get_all_sessions(user_id)
    if sessions:
        print(f"\n您有 {len(sessions)} 个历史会话")
        print("会话列表：", ", ".join(sessions[-3:]))
        choice = input("\n继续上次对话？（y/n）").strip().lower()
        if choice == "y":
            session_id = sessions[-1]
            print(f" 继续会话：{session_id}")
        else:
            session_id = None
            print("开始新会话")
    else:
        session_id = None
        print(f"\n 欢迎新客户：{user_id}")
    
    bot.start_session(user_id, session_id)
    
    if bot.messages:
        print(f"\n {bot.messages[-1].content}\n")
    
    print("输入 quit 结束对话\n")
    
    while True:
        user_input = input("> user: ")
        if user_input.strip() == "quit":
            bot.end_session()
            print(f"\n 对话已保存")
            print(f"会话ID： {bot.current_user}")
            print("感谢使用，再见！")
            break
        if not user_input.strip():
            continue
        
        response = bot.chat(user_input)
        print(f"客服： {response}")


if __name__ == '__main__':
    main()
