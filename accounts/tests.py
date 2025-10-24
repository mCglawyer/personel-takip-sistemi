# accounts/tests.py

from django.test import TestCase
# Test etmek istediğimiz modelleri import ediyoruz
from .models import Branch, User # Şimdilik Branch ve User yeterli

# Testlerimizi gruplamak için Test Case'ler oluştururuz
# İsimlendirme genellikle ModelAdiTests şeklinde olur
class BranchModelTests(TestCase):

    # Her test fonksiyonu 'test_' ile başlamalıdır
    def test_branch_creation_and_str(self):
        """
        Branch modelinin doğru şekilde oluşturulup oluşturulmadığını
        ve __str__ metodunun doğru ismi döndürüp döndürmediğini test eder.
        """
        # 1. Test verisi oluşturma (Arrange)
        branch_name = "Merkez Şube Test"
        branch = Branch.objects.create(name=branch_name)

        # 2. Test edilecek işlemi yapma (Act)
        # Bu testte __str__ metodunu test ediyoruz
        branch_str_representation = str(branch)

        # 3. Sonucu doğrulama (Assert)
        # Beklenen sonuç ile gerçekleşen sonucu karşılaştır
        self.assertEqual(branch_str_representation, branch_name)
        # Ayrıca, objenin veritabanında gerçekten oluştuğunu da kontrol edebiliriz
        self.assertEqual(Branch.objects.count(), 1)
        retrieved_branch = Branch.objects.get(id=branch.id)
        self.assertEqual(retrieved_branch.name, branch_name)

# Buraya gelecekte diğer modeller (Break, Shift, Profile, LeaveRequest) için
# ve view fonksiyonları için yeni Test Case'ler (class'lar) eklenecek.
# Örn: class BreakModelTests(TestCase): ...
# Örn: class LoginViewTests(TestCase): ...