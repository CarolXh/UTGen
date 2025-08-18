# 环境准备

# 安装依赖
pip install -r requirements.txt

# 安装java环境
1. 镜像版本：JDK 17 LTS
2. 安装并配置环境变量
3. 下载 JUnit5 ConsoleLauncher
    打开 https://search.maven.org → 搜  junit-platform-console-standalone 
    下载  junit-platform-console-standalone-1.10.x.jar 
    放到项目目录  junit_libs/  下即可

# 安装maven
1. 下载 Maven
   打开 https://maven.apache.org/download.cgi → 下载 Binary zip archive
2. 解压并配置环境变量

# 准备项目环境
1. 对已有java项目，直接解压
2. 对新创建的项目，使用maven创建

# 数据准备
多个代码文件到文档的反向生成,以及知识库存储（如果已经建立有相关数据库，可以跳过，faiss默认目录在unit_test_gen\data_preparation\db_data下）：
在unit_test目录下，执行：
python -m unit_test_gen.data_preparation.test_db 
参数选项： 
--src_proj_dir [optional] 待测项目根目录（不包含test目录）

# 开始运行
在unit_test目录下，执行：
python -m unit_test_gen.ut_case_generation.test_gen 
参数选项详见 --help
默认情况下只需要改filename即可。后续逐渐提供批处理支持。

