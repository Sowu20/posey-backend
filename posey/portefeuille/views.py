import uuid
import requests
import logging
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from portefeuille.models import Portefeuille, Transaction
from portefeuille.serializers import PortefeuilleSerializer, TransactionSerializer, ListeTransactionStatutSerializer, ListeTransactionSerializer
from django.db import models
from django.contrib.auth.models import User
from users.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

PAYGATE_API_URL = "https://paygateglobal.com/api/v1/pay"
PAYGATE_AUTH_TOKEN = "38710af9-f48a-460f-9cc8-17ee424b7b34"

class FairePaiementView(APIView):
    @swagger_auto_schema(
        operation_description="Effectue un paiement via PayGate.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user_id", "phone_number", "amount", "network"],
            properties={
                "user_id": openapi.Schema(type=openapi.TYPE_STRING, description="ID de l'utilisateur"),
                "phone_number": openapi.Schema(type=openapi.TYPE_STRING, description="Numéro de téléphone (ex: 70123456)"),
                "amount": openapi.Schema(type=openapi.TYPE_NUMBER, description="Montant à payer"),
                "network": openapi.Schema(type=openapi.TYPE_STRING, enum=["FLOOZ", "TMONEY"], description="Réseau de paiement"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, description="Description de la transaction", default="Achat via plateforme"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Paiement lancé avec succès",
                examples={
                    "application/json": {
                        "message": "Paiement lancé avec succès. Veuillez valider sur votre téléphone.",
                        "transaction": {
                            "id": 1,
                            "montant": "1000.00",
                            "statut": "en_attente",
                            "identifier": "uuid-string"
                        }
                    }
                }
            ),
            400: "Erreur de validation"
        }
    )
    def post(self, request):
        try:
            # Récupération des données avec les bons noms de champs
            user_id = request.data.get("user_id")
            phone_number = request.data.get("phone_number")
            amount = request.data.get("amount")
            network = request.data.get("network")
            description = request.data.get("description", "Achat via plateforme")
            
            # Validation des champs obligatoires
            if not all([user_id, phone_number, amount, network]):
                missing_fields = []
                if not user_id: missing_fields.append("user_id")
                if not phone_number: missing_fields.append("phone_number")
                if not amount: missing_fields.append("amount")
                if not network: missing_fields.append("network")
                
                return Response({
                    "detail": f"Champs manquants: {', '.join(missing_fields)}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validation et conversion du montant
            try:
                amount = Decimal(str(amount))
                if amount <= 0:
                    return Response({
                        "detail": "Le montant doit être positif."
                    }, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                return Response({
                    "detail": "Format de montant invalide."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validation du réseau
            if network not in ["FLOOZ", "TMONEY"]:
                return Response({
                    "detail": "Réseau non supporté. Utilisez FLOOZ ou TMONEY."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validation du numéro de téléphone
            if not self._validate_phone_number(phone_number, network):
                return Response({
                    "detail": "Format de numéro de téléphone invalide pour ce réseau."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Récupération de l'utilisateur
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    "detail": "Utilisateur introuvable."
                }, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({
                    "detail": "ID utilisateur invalide."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Création ou récupération du portefeuille
            portefeuille, created = Portefeuille.objects.get_or_create(user=user)
            
            # Génération de l'identifiant unique
            identifier = str(uuid.uuid4())
            
            # Enregistrement de la transaction locale en attente
            transaction = Transaction.objects.create(
                portefeuille=portefeuille,
                montant=amount,
                methode_payement=network,
                telephone=phone_number,
                statut=2,
                identifier=identifier,
                description=description
            )
            
            # Préparation de la payload pour PayGate
            payload = {
                "auth_token": PAYGATE_AUTH_TOKEN,
                "phone_number": phone_number,
                "amount": float(amount),
                "identifier": identifier,
                "network": network
            }
            
            # Log pour debug (sans le token)
            logger.info(f"Requête PayGate - Référence: {identifier}, Montant: {amount}, Réseau: {network}, Téléphone: {phone_number}")
            
            # Requête à PayGate avec gestion d'erreur
            try:
                response = requests.post(
                    PAYGATE_API_URL, 
                    json=payload,
                    timeout=30,
                    headers={'Content-Type': 'application/json'}
                )
                
                logger.info(f"Réponse PayGate Status Code: {response.status_code}")
                logger.info(f"Réponse PayGate Content: {response.text}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur de requête PayGate: {str(e)}")
                transaction.statut = -1
                transaction.save()
                return Response({
                    "detail": "Erreur de communication avec PayGate.",
                    "error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Traitement de la réponse
            try:
                paygate_response = response.json()
            except ValueError as e:
                logger.error(f"Réponse PayGate invalide (non JSON): {response.text}")
                transaction.statut = -1
                transaction.save()
                return Response({
                    "detail": "Réponse PayGate invalide.",
                    "raw_response": response.text
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Vérification du statut de la réponse
            if response.status_code == 200 and paygate_response.get("status") == 0:
                transaction.reference_externe = paygate_response.get("tx_reference")
                transaction.save()
                
                logger.info(f"Paiement lancé avec succès - Référence: {identifier}")
                
                return Response({
                    "message": "Paiement lancé avec succès. Veuillez valider sur votre téléphone.",
                    "transaction": {
                        "id": transaction.id,
                        "montant": str(transaction.montant),
                        "statut": transaction.statut,
                        "identifier": transaction.identifier,
                        "reference_externe": transaction.reference_externe,
                        "methode_payement": transaction.methode_payement,
                        "telephone": transaction.telephone
                    },
                    "paygate_response": paygate_response
                }, status=status.HTTP_200_OK)
            else:
                # Gestion des erreurs PayGate
                error_message = self._get_paygate_error_message(paygate_response.get("status"))
                transaction.statut = -1
                transaction.save()
                
                logger.error(f"Échec PayGate - Statut: {paygate_response.get('status')}, Message: {error_message}")
                
                return Response({
                    "detail": error_message,
                    "paygate_response": paygate_response
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Erreur inattendue dans FairePaiementView: {str(e)}")
            return Response({
                "detail": "Une erreur inattendue s'est produite.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _validate_phone_number(self, phone_number, network):
        """Valide le format du numéro de téléphone selon le réseau"""
        if not phone_number:
            return False
        
        # Supprime les espaces et caractères spéciaux
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        
        if network == "FLOOZ":
            # Format Flooz: commence par 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99
            return len(clean_phone) == 8 and clean_phone.startswith(('90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79'))
        elif network == "TMONEY":
            # Format T-Money: commence par 90, 91, 92, 93, 94, 95, 96, 97, 98, 99
            return len(clean_phone) == 8 and clean_phone.startswith(('70', '71', '72', '73', '74', '75', '76', '77', '78', '79','90', '91', '92', '93', '94', '95', '96', '97', '98', '99'))
        
        return False
    
    def _get_paygate_error_message(self, status_code):
        """Retourne un message d'erreur lisible selon le code de statut PayGate"""
        error_messages = {
            1: "Paramètres manquants ou invalides.",
            2: "Token d'authentification invalide.",
            3: "Montant invalide.",
            4: "Numéro de téléphone invalide.",
            5: "Réseau non supporté.",
            6: "Erreur de configuration ou service temporairement indisponible."
        }
        
        return error_messages.get(status_code, f"Erreur PayGate inconnue (code: {status_code})")
        
class VerifierPaiementView(APIView):
    @swagger_auto_schema(
        operation_description="Vérifie l'état d'une transaction PayGate.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["tx_reference"],
            properties={
                "tx_reference": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
        responses={200: "Statut mis à jour", 400: "Erreur de vérification"}
    )
    def post(self, request):
        tx_reference = request.data.get("tx_reference")
        
        if not tx_reference:
            return Response({
                "message": "La référence de transaction est requise."
            }, status=400)
            
        url_verification = "https://paygateglobal.com/api/v1/status" 
        payload = {"tx_reference": tx_reference}

        try:
            response = requests.post(
                url_verification,
                headers={
                    "Authorization": f"Bearer {PAYGATE_AUTH_TOKEN}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

            if response.status_code != 200:
                return Response({
                    "message": "Erreur lors de la requête PayGate",
                    "status_code": response.status_code,
                    "response_text": response.text
                }, status=400)

            try:
                data = response.json()
            except ValueError:
                return Response({
                    "message": "Réponse invalide de PayGate (non JSON)",
                    "contenu": response.text
                }, status=400)

            # Debug logs
            print("Réponse PayGate", data)
            
            # Vérifier d'abord s'il y a une erreur dans la réponse PayGate
            if 'error_code' in data:
                error_code = data.get('error_code')
                error_message = data.get('error_message', 'Erreur inconnue')
                
                print(f"Erreur PayGate - Code: {error_code}, Message: {error_message}")
                
                # Gérer les différents codes d'erreur PayGate
                if error_code == 403:
                    return Response({
                        "message": f"Erreur PayGate: {error_message}",
                        "error_code": error_code,
                        "tx_reference": tx_reference
                    }, status=400)
                elif error_code == 404:
                    return Response({
                        "message": "Transaction non trouvée chez PayGate",
                        "error_code": error_code,
                        "tx_reference": tx_reference
                    }, status=404)
                else:
                    return Response({
                        "message": f"Erreur PayGate: {error_message}",
                        "error_code": error_code,
                        "tx_reference": tx_reference
                    }, status=400)

            statut_paygate = data.get("status")
            print("Statut brut:", statut_paygate)
            print("Type statut:", type(statut_paygate))
            
            if statut_paygate is None:
                return Response({
                    "message": "Statut de transaction manquant dans la réponse PayGate",
                    "paygate_response": data,
                    "tx_reference": tx_reference
                }, status=400)

            try:
                transaction = Transaction.objects.get(reference_externe=tx_reference)
            except Transaction.DoesNotExist:
                return Response({
                    "message": "Transaction introuvable dans notre système.",
                    "tx_reference": tx_reference
                }, status=404)

            portefeuille = transaction.portefeuille
            ancien_statut = transaction.statut

            if statut_paygate == 0: 
                if transaction.statut != 0:
                    transaction.statut = 0
                    transaction.save()

                    if ancien_statut != 0:
                        portefeuille.solde += transaction.montant
                        portefeuille.save()

                return Response({
                    "message": "Paiement confirmé.",
                    "tx_reference": transaction.reference_externe,
                    "reference": transaction.identifier,
                    "statut": 0,
                    "date_transaction": transaction.date_transaction,
                    "methode_payement": transaction.methode_payement,
                    "solde_utilisateur": portefeuille.solde
                }, status=200)

            elif statut_paygate == 2:  
                if transaction.statut != 2:
                    transaction.statut = 2
                    transaction.save()
                    
                return Response({
                    "message": "Paiement en cours.",
                    "tx_reference": transaction.reference_externe,
                    "reference": transaction.identifier,
                    "statut": 2,
                    "date_transaction": transaction.date_transaction,
                    "methode_payement": transaction.methode_payement
                }, status=200)

            elif statut_paygate == 4: 
                if transaction.statut != 4:
                    transaction.statut = 4
                    transaction.save()
                    
                return Response({
                    "message": "Paiement expiré.",
                    "tx_reference": transaction.reference_externe,
                    "reference": transaction.identifier,
                    "statut": 4,
                    "date_transaction": transaction.date_transaction,
                    "methode_payement": transaction.methode_payement
                }, status=200)

            elif statut_paygate == 6:  
                if transaction.statut != 6:
                    transaction.statut = 6
                    transaction.save()
                    
                return Response({
                    "message": "Paiement annulé.",
                    "tx_reference": transaction.reference_externe,
                    "reference": transaction.identifier,
                    "statut": 6,
                    "date_transaction": transaction.date_transaction,
                    "methode_payement": transaction.methode_payement
                }, status=200)

            else: 
                if transaction.statut != -1:
                    transaction.statut = -1
                    transaction.save()
                    
                return Response({
                    "message": "Paiement échoué.",
                    "tx_reference": transaction.reference_externe,
                    "reference": transaction.identifier,
                    "statut": -1,
                    "date_transaction": transaction.date_transaction,
                    "methode_payement": transaction.methode_payement
                }, status=200)

        except requests.RequestException as e:
            return Response({
                "message": f"Erreur de connexion à PayGate: {str(e)}"
            }, status=500)
        except Exception as e:
            return Response({
                "message": f"Erreur interne: {str(e)}"
            }, status=500)
        
class VerifierTransactionView(APIView):
    @swagger_auto_schema(
        operation_description="Vérifie le statut d'une transaction.",
        manual_parameters=[
            openapi.Parameter('identifier', openapi.IN_QUERY, description="Identifiant de la transaction", type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: "Statut de la transaction", 404: "Transaction non trouvée"}
    )
    def get(self, request):
        identifier = request.query_params.get('identifier')
        
        if not identifier:
            return Response({
                "detail": "Paramètre 'identifier' requis."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            transaction = Transaction.objects.get(identifier=identifier)
            return Response({
                "transaction": TransactionSerializer(transaction).data
            }, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({
                "detail": "Transaction non trouvée."
            }, status=status.HTTP_404_NOT_FOUND)
        
class ConsulterSoldeView(APIView):
    queryset = User.objects.all()
    serializer_class = PortefeuilleSerializer
    lookup_field = 'id'
    @swagger_auto_schema(
        operation_description="Consulte le solde du portefeuille d'un utilisateur.",
        responses={
            200: openapi.Response(description="Solde retourné avec succès"),
            404: "Utilisateur ou portefeuille introuvable"
        }
    )
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
            portefeuille = Portefeuille.objects.get(user=user)
            return Response({
                "id": user.id,
                "nom_utilisateur": user.username,
                "solde": portefeuille.solde
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"message": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        except Portefeuille.DoesNotExist:
            return Response({"message": "Portefeuille introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
class ListeTransactionsView(APIView):
    @swagger_auto_schema(
        operation_description="Liste toutes les transactions d'un utilisateur.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user_id"],
            properties={
                "user_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        responses={200: "Liste des transactions"}
    )
    def post(self, request):
        user_id = request.data.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            portefeuille = Portefeuille.objects.get(user=user)
            transactions = Transaction.objects.filter(portefeuille=portefeuille).order_by("-date_transaction")
            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data, status=200)

        except User.DoesNotExist:
            return Response({"message": "Utilisateur introuvable."}, status=404)
        except Portefeuille.DoesNotExist:
            return Response({"message": "Portefeuille introuvable."}, status=404)
        
class ListeTransactionView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = ListeTransactionSerializer

    @swagger_auto_schema(
        responses={201: "Liste des utilisateurs", 400: "Données invalides"}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ListeTransactionStatutView(generics.ListAPIView):
    serializer_class = ListeTransactionStatutSerializer

    def get_queryset(self):
        statut = self.request.query_params.get('statut')
        valid_statut = ['en attente', 'succes', 'echec', 'annule']
        if statut in valid_statut:
            return Transaction.objects.filter(statut=statut)
        return Transaction.objects.filter(statut__in=valid_statut)
    
class TransactionsUtilisateurView(APIView):
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
            portefeuille = Portefeuille.objects.get(user=user)
            transactions = Transaction.objects.filter(portefeuille=portefeuille).order_by('-date_transaction')
            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        except Portefeuille.DoesNotExist:
            return Response({"message": "Portefeuille introuvable pour cet utilisateur."}, status=status.HTTP_404_NOT_FOUND)
        
class PayGateWebhookView(APIView):
    def post(self, request):
        try:
            data = request.data
            logger.info(f"Webhook PayGate reçu: {data}")
           
            tx_reference = data.get("tx_reference")
            status_code = data.get("status")
            reference = data.get("reference")
           
            if not reference:
                logger.error("Webhook PayGate: référence manquante")
                return Response({
                    "detail": "Référence manquante."
                }, status=status.HTTP_400_BAD_REQUEST)
           
            if status_code is None:
                logger.error("Webhook PayGate: status_code manquant")
                return Response({
                    "detail": "Status code manquant."
                }, status=status.HTTP_400_BAD_REQUEST)
           
            try:
                transaction = Transaction.objects.get(identifier=reference)
                ancien_statut = transaction.statut
                
                logger.info(f"Transaction trouvée: {reference}, ancien statut: {ancien_statut}, nouveau statut: {status_code}")
               
                if status_code == 0:  # Succès
                    transaction.statut = 0
                    if tx_reference:
                        transaction.reference_externe = tx_reference
                    
                    # Ajouter le montant au portefeuille seulement si ce n'était pas déjà fait
                    if ancien_statut != 0:
                        transaction.portefeuille.solde += transaction.montant
                        transaction.portefeuille.save()
                        logger.info(f"Solde mis à jour pour {reference}: +{transaction.montant}")
                    
                elif status_code == 2:  # En attente
                    transaction.statut = 2
                elif status_code == 4:  # Expiré
                    transaction.statut = 4
                elif status_code == 6:  # Annulé
                    transaction.statut = 6
                else:  # Autres = Échec
                    transaction.statut = -1
                
                transaction.save()
                logger.info(f"Transaction {reference} mise à jour avec le statut {status_code}")
               
                return Response({
                    "message": "Webhook traité avec succès.",
                    "transaction_id": reference,
                    "new_status": status_code
                }, status=status.HTTP_200_OK)
               
            except Transaction.DoesNotExist:
                logger.error(f"Transaction introuvable pour la référence: {reference}")
                return Response({
                    "detail": f"Transaction introuvable pour la référence: {reference}"
                }, status=status.HTTP_404_NOT_FOUND)
               
        except Exception as e:
            logger.error(f"Erreur dans PayGateWebhookView: {str(e)}")
            return Response({
                "detail": "Erreur lors du traitement du webhook.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)