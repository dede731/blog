from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Post, Category

app = create_app('default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Post=Post, Category=Category)

@app.cli.command('init_db')
def init_db():
    """初始化数据库"""
    db.create_all()
    print('数据库初始化完成')

@app.cli.command('create_admin')
def create_admin():
    """创建管理员用户"""
    username = input('请输入管理员用户名: ')
    email = input('请输入管理员邮箱: ')
    password = input('请输入管理员密码: ')
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        print(f'用户名 "{username}" 已存在！')
        return
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=email).first():
        print(f'邮箱 "{email}" 已存在！')
        return
    
    # 创建管理员用户
    admin_user = User(
        username=username,
        email=email,
        is_admin=True
    )
    admin_user.set_password(password)
    
    db.session.add(admin_user)
    db.session.commit()
    
    print(f'管理员用户 "{username}" 创建成功！')
    print(f'邮箱: {email}')
    print('请使用此账户登录管理后台。')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init_db':
            with app.app_context():
                db.create_all()
                print('数据库初始化完成')
        elif sys.argv[1] == 'create_admin':
            with app.app_context():
                create_admin()
        else:
            print(f'未知的命令: {sys.argv[1]}')
            print('可用命令:')
            print('  init_db      - 初始化数据库')
            print('  create_admin - 创建管理员用户')
    else:
        app.run(host='0.0.0.0', port=5000)