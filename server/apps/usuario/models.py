from django.db import models    # Biblioteca para criação de modelos de tabelas
from django.core.exceptions import ValidationError # Biblioteca para validação de dados
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator # Biblioteca para validação de dados

# O CustomUserManager serve para gerenciar os usuários no Django e estende a classe UserManager.
# O gerenciador de usuários é responsável por criar e salvar usuários, além de definir superusuários.
class CustomUserManager(UserManager):

    # Método responsável por criar e salvar um usuário comum.
    def _create_user(self, email, password, **extra_fields):

        # Verifica se um e-mail foi fornecido.
        if not email:
            raise ValueError("O e-mail disponibilizado não é válido!")
        
        email = self.normalize_email(email) # Essa função serve para garantir que o e-mail esteja no formato correto.
        user = self.model(email=email, **extra_fields) # Criação de um objeto usuário.
        user.set_password(password) # Define a senha do usuário.
        user.save(using=self._db) # Salva o usuário no banco de dados.
        return user
    
    # Esse método chama o método de criar usuário e cria um usuário comum com algumas permissões padrões.
    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
        
    
    # Esse método chama o método de criar usuário e cria um superusuário com privilégios.
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


# Criação do modelo do User.
# AbstractUser e PermissionsMixin fornecem funcionalidades básicas para isso.
class User(AbstractBaseUser, PermissionsMixin):
        
    def validar_cpf(valor):
        """
        Essa função serve para verificar se um CPF é válido, 
        desde a sua formatação, até seu cálculo numérico de validação!
        """
        if (len(valor) != 14 or not valor.replace(".", "").replace("-", "").isdigit()):
            raise ValidationError('O CPF está no formato incorreto, ele deve estar no formato "xxx.xxx.xxx-xx".')
        else:
            cpf_completo = valor.replace(".", "").replace("-", "")
            cpf_digitos = [int(cpf_completo[i]) for i in range(0, 11)]

            # soma_digitos realiza a soma conforme o cálculo númerico de verificação de um CPF
            # cpf_array corresponde a um array com cada digito do CPF.
            # cpf_quant_digitos corresponde a com quantos digitos será feito o cálculo, com base na etapa em que ele se encontra.
            # Pois, por exemplo, depois de calcular os nove primeiros digitos, e descobrir o primeiro digito verificador, 
            # agora será um cálculo com 10 números.
            # verifica_modulo faz a validação para descobrir os digitos verificadores.
            
            soma_digitos = lambda cpf_array, cpf_quant_digitos: sum(cpf_array[i] * (cpf_quant_digitos+1-i) for i in range(0, cpf_quant_digitos))
            verifica_modulo = lambda soma: 0 if (soma % 11 == 0 or soma % 11 == 1) else 11 - (soma % 11)

            primeiro_digito_verificador = verifica_modulo(soma_digitos(cpf_digitos, 9))
            segundo_digito_verificador = verifica_modulo(soma_digitos(cpf_digitos, 10))

            if (primeiro_digito_verificador != cpf_digitos[9] or segundo_digito_verificador != cpf_digitos[10]):
                raise ValidationError('O CPF é inválido!')
    
    def validar_texto(valor):
        """
        Essa função serve para verificar se um texto tem um tamanho válido
        """
        nome_completo = valor.split(" ")
        if (len(nome_completo) < 2):
            raise ValidationError('Campo Insuficiente')
        else:
            for nome in nome_completo:
                if (len(nome) < 2):
                    raise ValidationError('Campo Insuficiente')
            
    
    SEXO_CHOICES = ( # Lista de opções para o campo de gênero
        ('Masculino', 'Masculino'),
        ('Feminino', 'Feminino'),
        ('Outro', 'Outro'),
    )
    
    ESTADO_CIVIL_CHOICES = ( # Lista de opções para o campo de estado civil
        ('Solteiro(a)', 'Solteiro(a)'),
        ('Casado(a)', 'Casado(a)'),
        ('Divorciado(a)', 'Divorciado(a)'),
        ('Viúvo(a)', 'Viúvo(a)'),
    )

    nome = models.CharField(max_length=500, validators=[RegexValidator(r'^[a-zA-ZÀ-ÿ\s]*$', 
                                                                       message='Nome Completo deve conter apenas letras'), validar_texto], 
                            null=False, blank=False, verbose_name='Nome do Usuário', help_text="Digite o seu nome completo")
    
    cpf = models.CharField(max_length=14, unique=True, null=False, blank=False, verbose_name='CPF', validators=[validar_cpf], 
                           help_text="Digite seu CPF e no formato XXX.XXX.XXX-XX")
    
    email = models.EmailField(max_length=500, unique=True, verbose_name='E-mail', help_text="Digite o seu e-mail")              
    
    genero = models.CharField(max_length=10, null=True, blank=True, choices=SEXO_CHOICES,
                              verbose_name='Gênero', help_text="Digite o seu gênero")
    
    estado_civil = models.CharField(max_length=15, null=True, blank=True, choices=ESTADO_CIVIL_CHOICES,
                                    verbose_name='Estado Civil', help_text="Digite o seu estado civil")
    
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False, verbose_name='Data de Criação')
    
    telefone = models.CharField(max_length=19, 
                                validators=[RegexValidator(r'\([0-9]{2}\) [0-9]{5}-[0-9]{4}', message='Digite um telefone válido com DDD')],
                                unique=True, null=True, blank=True, help_text="número de telefone no formato (XX) XXXXX-XXXX")
    
    
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    is_staff = models.BooleanField(default=True,  verbose_name="Staff")
    is_superuser = models.BooleanField(default=False, verbose_name="Super-usuário")

    # É responsável por gerenciar os objetos do modelo.
    objects = CustomUserManager()

    USERNAME_FIELD = 'email' # Indica que o e-mail vai ser usado como o identificador exclusivo do usuário.
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['nome'] # Campos adicionais necessários na criação do usuário.

    def __str__(self):
        return self.nome
    
    # Retorna uma parte do nome para aparecer no perfil.
    def get_short_name(self):
        # Valores possíveis:
        # - Dois primeiros nomes caso tenha sido registrado 2 ou mais nomes e sobrenomes.
        # - Um único nome caso tenha sido apenas registrado um nome.
        # - O início do e-mail caso não tenha nome.
        return f"{self.nome.split(' ')[0]} {self.nome.split(' ')[1]}" if len(self.nome.split(' ')) >= 2 else f"{self.nome.split(' ')[0]}" if len(self.nome.split(' ')) != 0 else self.email.split('@')[0]


    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
